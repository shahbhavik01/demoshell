#!/usr/bin/env python

import subprocess
import urwid
import os
import sys

factor_me = 362923067964327863989661926737477737673859044111968554257667
run_me = os.path.join(os.path.dirname(sys.argv[0]), 'subproc2.py')

palette = [
    ('spacer', 'white', 'white'),
    ('stdout', 'black', 'white'),
    ('command', 'black', 'light gray'),
    ('error', 'light red', 'black'),
]

output_widget = urwid.Text(markup='')
prompt_widget = urwid.Edit("$ ")
frame_widget = urwid.Frame(
    header=prompt_widget,
    body=urwid.Filler(output_widget, valign='top'),
    focus_part='header',
)

def on_enter(key):
    if key == 'enter':
        cmd = prompt_widget.text
        cmd = cmd.lstrip('$ ')
        if cmd == 'exit':
            raise urwid.ExitMainLoop()
        extend_text(output_widget, 'command', cmd + '\n')
        write_fd = loop.watch_pipe(received_output)
        proc = subprocess.Popen(
            cmd,
            stdout=write_fd,
            stderr=subprocess.STDOUT,
            close_fds=True,
            shell=True,
        )
        prompt_widget.set_edit_text('')
    elif key == 'ctrl d':
        raise urwid.ExitMainLoop()
    else:
        extend_text(output_widget, 'error',
                    'Unknown keypress {!r}'.format(key))


def extend_text(widget, style, text):
    existing = widget.get_text()
    parts = []
    start = 0
    existing_text = existing[0]
    for attr, count in existing[1]:
        parts.append((attr, existing_text[start:start+count]))
        start += count
    if style == 'command':
        # insert a new command entry and an empty stdout entry, in
        # reverse order because we're pushing them onto the front of
        # the list
        parts.insert(0, ('stdout', ''))
        parts.insert(0, (style, text))
        parts.insert(0, ('spacer', '\n'))
    elif style == 'error':
        parts.insert(0, (style, text.rstrip() + '\n'))
    elif style == 'stdout':
        loc = None
        for i, p in enumerate(parts):
            if p[0] == 'stdout':
                loc = i
                break
        else:
            raise RuntimeError('did not find stdout block')
        new_text = parts[loc][1] + text
        parts[loc] = (parts[loc][0], new_text)
    else:
        raise ValueError('unknown style {} used for {!r}'.format(style, text))
    widget.set_text(parts)


def received_output(data):
    extend_text(output_widget, 'stdout', data.decode('utf-8'))


loop = urwid.MainLoop(
    frame_widget,
    unhandled_input=on_enter,
    palette=palette,
)

loop.run()
