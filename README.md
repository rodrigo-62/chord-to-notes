# chord-to-notes

Parses and translates musical chords into lists of notes.
Built with Python and PLY (lex/yacc) to handle:
- twelve-tone equal temperament
- enharmonic spelling (supports double accidentals)
- extended and altered voicings (9ths, 13ths, b5, #9, etc.)
- inversions, slash chords, and added bass notes
- suspensions, additions, and omissions

## usage

`python chord_to_notes.py`

```txt
> C(#5)
  C - E - G#

> F#m7b5
  F# - A - C - E

> G+Maj7(#11)/B
  B - G - D# - F# - C#
```

