import sys
import chimerax.core.commands as ccc

print(sys.argv)
input_file = sys.argv[1]
output_file = sys.argv[2]

rotation_list = [
    [0, 0],
    [0, 90],
    [90, 90],
    [180, 0]
    ]

for list_index in range(4):
    volume_index = list_index + 1
    ccc.run(session, 'open {}'.format(input_file))
    ccc.run(session, 'volume #{} step 1'.format(volume_index))
    ccc.run(session, 'volume #{} sdLevel 5'.format(volume_index))
    ccc.run(session, 'turn z {} models #{}'.format(rotation_list[list_index][0], volume_index))
    ccc.run(session, 'turn x {} models #{}'.format(rotation_list[list_index][1], volume_index))

ccc.run(session, 'windowsize 800 800')
ccc.run(session, 'set bgColor white')
ccc.run(session, 'tile')
ccc.run(session, 'save {}'.format(output_file))
ccc.run(session, 'exit')
