// Reference-driven procedural drum engine for DTX Drum Flow.
// The attached Luna say maybe mix is used only as a timbral reference.
// No source audio is embedded, copied, or redistributed.

export const LUNA_LIVE_PRESET = Object.freeze({
  version: 1,
  name: "Luna Live Kit v1",
  master: { input: 0.9, output: 0.88, room: 0.22 },
  room: { earlyA: 0.017, earlyB: 0.043, lowpass: 7200 },
  kick: {
    bodyStartHz: 116, bodyEndHz: 47, bodyDecay: 0.29,
    subHz: 62, subEndHz: 41, subDecay: 0.34,
    beaterHz: 2900, beaterDecay: 0.026
  },
  snare: {
    shellHz: 194, shellEndHz: 128, shellDecay: 0.19,
    ringHz: 322, ringDecay: 0.1,
    wireHz: 2050, wireDecay: 0.24,
    airHz: 5600, airDecay: 0.12
  },
  sideStick: { bodyHz: 1110, clickHz: 2080, decay: 0.06 },
  hihat: {
    closedDecay: 0.105, openDecay: 0.76,
    highpassHz: 6900, bandHz: 9800,
    partials: [5480, 6940, 8230, 10120]
  },
  toms: {
    HT: { fundamentalHz: 174, decay: 0.35, attackNoiseHz: 1850 },
    LT: { fundamentalHz: 132, decay: 0.43, attackNoiseHz: 1380 },
    FT: { fundamentalHz: 96, decay: 0.54, attackNoiseHz: 920 }
  },
  ride: {
    decay: 0.74,
    partials: [2360, 4010, 6420],
    washHighpassHz: 5200
  },
  crash: {
    decay: 1.8,
    leftPartials: [3260, 4310, 5720, 7460, 9820],
    rightPartials: [3510, 4680, 6140, 8030, 10400],
    washHighpassHz: 3300
  },
  humanize: { velocityMin: 0.94, velocityMax: 1.04, detuneCents: 10 }
});

const clamp = (value, min, max) => Math.max(min, Math.min(max, value));

export class LiveDrumEngine {
  constructor(audioContext, destination, preset = LUNA_LIVE_PRESET) {
    this.ctx = audioContext;
    this.destination = destination;
    this.preset = preset;
    this.nodes = new Set();
    this._buildBus();
  }

  _buildBus() {
    const ctx = this.ctx;
    const input = ctx.createGain();
    const close = ctx.createGain();
    const room = ctx.createGain();
    const delayA = ctx.createDelay(0.25);
    const delayB = ctx.createDelay(0.25);
    const roomFilter = ctx.createBiquadFilter();
    const compressor = ctx.createDynamicsCompressor();
    const output = ctx.createGain();

    input.gain.value = this.preset.master.input;
    close.gain.value = 0.82;
    room.gain.value = this.preset.master.room;
    delayA.delayTime.value = this.preset.room.earlyA;
    delayB.delayTime.value = this.preset.room.earlyB;
    roomFilter.type = "lowpass";
    roomFilter.frequency.value = this.preset.room.lowpass;

    compressor.threshold.value = -17;
    compressor.knee.value = 16;
    compressor.ratio.value = 3.2;
    compressor.attack.value = 0.003;
    compressor.release.value = 0.13;
    output.gain.value = this.preset.master.output;

    input.connect(close);
    close.connect(compressor);
    input.connect(delayA);
    input.connect(delayB);
    delayA.connect(roomFilter);
    delayB.connect(roomFilter);
    roomFilter.connect(room);
    room.connect(compressor);
    compressor.connect(output);
    output.connect(this.destination);

    this.input = input;
    this.output = output;
  }

  _track(node) {
    this.nodes.add(node);
    node.addEventListener?.("ended", () => this.nodes.delete(node), { once: true });
    return node;
  }

  stop() {
    for (const node of this.nodes) {
      try { node.stop(); } catch {}
    }
    this.nodes.clear();
  }

  _noiseBuffer(seconds) {
    const length = Math.max(1, Math.round(this.ctx.sampleRate * seconds));
    const buffer = this.ctx.createBuffer(1, length, this.ctx.sampleRate);
    const data = buffer.getChannelData(0);
    let coloured = 0;
    for (let i = 0; i < length; i++) {
      const white = Math.random() * 2 - 1;
      coloured = coloured * 0.72 + white * 0.28;
      data[i] = white * 0.72 + coloured * 0.28;
    }
    return buffer;
  }

  _envelope(time, peak, attack, decay) {
    const gain = this.ctx.createGain();
    gain.gain.setValueAtTime(0.0001, time);
    gain.gain.exponentialRampToValueAtTime(Math.max(0.0002, peak), time + attack);
    gain.gain.exponentialRampToValueAtTime(0.0001, time + decay);
    gain.connect(this.input);
    return gain;
  }

  _tone({ time, frequency, endFrequency, decay, gain, type = "sine", attack = 0.001, detune = 0 }) {
    const oscillator = this.ctx.createOscillator();
    const envelope = this._envelope(time, gain, attack, decay);
    oscillator.type = type;
    oscillator.frequency.setValueAtTime(frequency, time);
    oscillator.detune.value = detune;
    if (endFrequency) {
      oscillator.frequency.exponentialRampToValueAtTime(Math.max(20, endFrequency), time + decay * 0.72);
    }
    oscillator.connect(envelope);
    oscillator.start(time);
    oscillator.stop(time + decay + 0.03);
    this._track(oscillator);
  }

  _noise({ time, decay, gain, filterType, frequency, q = 0.7, attack = 0.001 }) {
    const source = this.ctx.createBufferSource();
    const filter = this.ctx.createBiquadFilter();
    const envelope = this._envelope(time, gain, attack, decay);
    source.buffer = this._noiseBuffer(decay + 0.05);
    filter.type = filterType;
    filter.frequency.value = frequency;
    filter.Q.value = q;
    source.connect(filter);
    filter.connect(envelope);
    source.start(time);
    source.stop(time + decay + 0.05);
    this._track(source);
  }

  _velocity(value) {
    const h = this.preset.humanize;
    return clamp(value * (h.velocityMin + Math.random() * (h.velocityMax - h.velocityMin)), 0.16, 1);
  }

  _partials(time, decay, gain, frequencies) {
    frequencies.forEach((frequency, index) => {
      this._tone({
        time: time + index * 0.0007,
        frequency,
        endFrequency: frequency * (0.82 + index * 0.018),
        decay: decay * (1 - index * 0.05),
        gain: gain / (1 + index * 0.38),
        type: index % 2 ? "sine" : "triangle",
        detune: (Math.random() - 0.5) * this.preset.humanize.detuneCents
      });
    });
  }

  trigger(part, velocity = 0.8, when = this.ctx.currentTime + 0.002, note = {}) {
    const t = Math.max(this.ctx.currentTime + 0.002, when);
    const v = this._velocity(clamp(velocity || 0.8, 0.18, 1));
    const gm = Number(note.gmNote);

    if (part === "SN" && gm === 37) return this._sideStick(t, v);
    if (part === "BD" || part === "LB") return this._kick(t, v);
    if (part === "SN") return this._snare(t, v);
    if (part === "HH" || part === "LP") return this._hihat(t, v, gm === 46);
    if (part === "HT" || part === "LT" || part === "FT") return this._tom(part, t, v);
    if (part === "RD") return this._ride(t, v);
    if (part === "LC" || part === "RC") return this._crash(part, t, v);
  }

  _kick(t, v) {
    const p = this.preset.kick;
    this._tone({ time: t, frequency: p.bodyStartHz, endFrequency: p.bodyEndHz, decay: p.bodyDecay, gain: 0.46 * v });
    this._tone({ time: t + 0.003, frequency: p.subHz, endFrequency: p.subEndHz, decay: p.subDecay, gain: 0.3 * v });
    this._noise({ time: t, decay: p.beaterDecay, gain: 0.11 * v, filterType: "bandpass", frequency: p.beaterHz, q: 1.4 });
  }

  _snare(t, v) {
    const p = this.preset.snare;
    this._tone({ time: t, frequency: p.shellHz, endFrequency: p.shellEndHz, decay: p.shellDecay, gain: 0.18 * v, type: "triangle" });
    this._tone({ time: t + 0.001, frequency: p.ringHz, endFrequency: 238, decay: p.ringDecay, gain: 0.05 * v });
    this._noise({ time: t, decay: p.wireDecay, gain: 0.31 * v, filterType: "bandpass", frequency: p.wireHz, q: 0.72 });
    this._noise({ time: t, decay: p.airDecay, gain: 0.15 * v, filterType: "highpass", frequency: p.airHz, q: 0.42 });
  }

  _sideStick(t, v) {
    const p = this.preset.sideStick;
    this._tone({ time: t, frequency: p.bodyHz, endFrequency: 780, decay: p.decay, gain: 0.19 * v, type: "triangle" });
    this._tone({ time: t + 0.001, frequency: p.clickHz, endFrequency: 1650, decay: 0.035, gain: 0.075 * v });
  }

  _hihat(t, v, open) {
    const p = this.preset.hihat;
    const decay = open ? p.openDecay : p.closedDecay;
    this._noise({ time: t, decay, gain: (open ? 0.16 : 0.155) * v, filterType: "highpass", frequency: p.highpassHz, q: 0.35 });
    this._noise({ time: t + 0.004, decay: decay * 0.72, gain: 0.085 * v, filterType: "bandpass", frequency: p.bandHz, q: 1.0 });
    this._partials(t, decay * 0.64, 0.02 * v, open ? p.partials : p.partials.slice(1));
  }

  _tom(part, t, v) {
    const p = this.preset.toms[part];
    const f = p.fundamentalHz;
    this._tone({ time: t, frequency: f * 1.28, endFrequency: f * 0.92, decay: p.decay * 0.58, gain: 0.16 * v, type: "triangle" });
    this._tone({ time: t + 0.001, frequency: f, endFrequency: f * 0.64, decay: p.decay, gain: 0.31 * v });
    this._tone({ time: t + 0.002, frequency: f * 2.02, endFrequency: f * 1.52, decay: p.decay * 0.48, gain: 0.055 * v });
    this._noise({ time: t, decay: 0.074, gain: 0.078 * v, filterType: "bandpass", frequency: p.attackNoiseHz, q: 1.05 });
  }

  _ride(t, v) {
    const p = this.preset.ride;
    this._partials(t, p.decay, 0.052 * v, p.partials);
    this._noise({ time: t, decay: p.decay, gain: 0.085 * v, filterType: "highpass", frequency: p.washHighpassHz, q: 0.48 });
  }

  _crash(part, t, v) {
    const p = this.preset.crash;
    this._noise({ time: t, decay: p.decay, gain: 0.16 * v, filterType: "highpass", frequency: p.washHighpassHz, q: 0.28 });
    this._noise({ time: t + 0.004, decay: p.decay * 0.62, gain: 0.075 * v, filterType: "bandpass", frequency: 6500, q: 0.65 });
    this._partials(t, p.decay * 0.75, 0.026 * v, part === "LC" ? p.leftPartials : p.rightPartials);
  }
}
