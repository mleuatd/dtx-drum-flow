#!/usr/bin/env python3
"""Enumerate actual flipbook actions from the final chart and limb assignments."""
import collections
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CHART = ROOT / 'site/charts/luna_say_maybe/Luna_say_maybe_FINAL_notes.json'
LIMBS = ROOT / 'site/charts/luna_say_maybe/Luna_say_maybe_full_limbs.json'
CONTACT = ROOT / 'character-assets/prototypes/luna_say_maybe_16m/INSTRUMENT_CONTACT_POINTS.json'
OUTPUT = Path(__file__).with_name('REQUIRED_ACTIONS.json')

def main():
    notes = json.loads(CHART.read_text())['notes']
    assignments = json.loads(LIMBS.read_text())['assignments']
    lookup = {(round(a['time'], 6), a['part']): a['limb'] for a in assignments}
    assert len(lookup) == len(assignments) == len(notes)
    enriched = []
    for n in notes:
        limb = lookup[(round(n['time'], 6), n['part'])]
        enriched.append((n, limb))
    enriched.sort(key=lambda x: x[0]['time'])
    groups = []
    for entry in enriched:
        if groups and (entry[0]['time'] - groups[-1][0][0]['time']) <= .008:
            groups[-1].append(entry)
        else:
            groups.append([entry])
    counts = collections.Counter()
    examples = {}
    for group in groups:
        key = ' + '.join(sorted(f"{n['part']}:{limb}" for n, limb in group))
        counts[key] += 1
        examples.setdefault(key, {'measure': group[0][0]['measure'], 'time': group[0][0]['time']})
    contacts = json.loads(CONTACT.read_text())['parts']
    targets = {k: v['approximate'] for k, v in contacts.items()}
    # The old HH point is an effect marker, not an observed stick-to-cymbal contact.
    targets['HH'] = {'x': 270, 'y': 425}
    actions = []
    for key, count in counts.most_common():
        parts = [{'part': n.split(':')[0], 'limb': n.split(':')[1],
                  'target': targets[n.split(':')[0]]} for n in key.split(' + ')]
        actions.append({'key': key, 'groups': count, 'firstOccurrence': examples[key],
                        'strikes': parts, 'frames': ['hit', 'rebound'],
                        'visualStatus': 'REBUILD_REQUIRED', 'stoolLock': True})
    result = {'schemaVersion': 1, 'canvas': [1448, 1086],
              'fixedDrum': 'character-assets/layers/drum/drum_base.png',
              'styleMaster': 'character-assets/layers/character/hh/hit_l.png',
              'styleRule': 'one consistent monochrome rough-pencil character and fixed stool; no old mixed-style frame promoted without full visual QA',
              'sourceChart': str(CHART.relative_to(ROOT)), 'limbAssignments': str(LIMBS.relative_to(ROOT)),
              'noteCount': len(notes), 'groupCount': len(groups), 'requiredActionCount': len(actions),
              'requiredNewFrames': len(actions)*2, 'actions': actions,
              'qa': ['correct actual limb', 'continuous shoulder-elbow-wrist-hand-stick',
                     'straight stick and visible contact on hit', 'natural same-action rebound',
                     'fixed stool and drum pixel alignment', 'same face-hair and clothing style',
                     'runtime maps exact action and phase']}
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    assert sum(a['groups'] for a in actions) == len(groups)
    print(f"{len(notes)} notes; {len(groups)} groups; {len(actions)} actions; {len(actions)*2} frames")

if __name__ == '__main__': main()
