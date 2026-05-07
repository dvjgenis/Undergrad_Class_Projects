# Note Editor Feature Comparison

**Purpose:** Ensure HarmonyForge Tactile Sandbox aligns with industry-standard notation editors (MuseScore, Noteflight, Flat, Dorico, Sibelius).

**Last updated:** March 2026

---

## Industry Standard Features (MuseScore / Flat / Dorico)

### Note Input & Editing
| Feature | MuseScore | Flat | HarmonyForge |
|---------|-----------|------|--------------|
| N = Note input mode | ✓ | ✓ | ✓ (Draw mode) |
| Esc = Exit input mode | ✓ | ✓ | ✓ (added) |
| Arrow Up/Down = semitone | ✓ | ✓ | ✓ (added) |
| Ctrl+Arrow = octave | ✓ | ✓ | ✓ (added) |
| 1–9 = Duration selection | ✓ | ✓ | ✓ (added: 1–6) |
| A–G = Pitch by letter | ✓ | ✓ | — (draw uses default) |
| 0 = Rest | ✓ | ✓ | — |
| R = Repeat note | ✓ | ✓ | — |
| Q/W = Half/double duration | ✓ | — | — |
| Click to add note | ✓ | ✓ | ✓ |
| Drag note for pitch | ✓ | ✓ | ✓ |

### Selection & Clipboard
| Feature | MuseScore | Flat | HarmonyForge |
|---------|-----------|------|--------------|
| Click to select | ✓ | ✓ | ✓ |
| Shift+click multi-select | ✓ | ✓ | ✓ |
| ⌘C / ⌘X / ⌘V | ✓ | ✓ | ✓ |
| Delete / Backspace | ✓ | ✓ | ✓ |

### Playback
| Feature | MuseScore | Flat | HarmonyForge |
|---------|-----------|------|--------------|
| Play/Pause | ✓ | ✓ | ✓ |
| VSTi / SoundFonts | ✓ | — | — (Tone.js sine) |
| Tempo control | ✓ | ✓ | — |

### Layout & Navigation
| Feature | MuseScore | Flat | HarmonyForge |
|---------|-----------|------|--------------|
| Zoom | ✓ | ✓ | ✓ |
| Page navigation | ✓ | ✓ | ✓ (mock) |
| Next/prev measure (Ctrl+←/→) | ✓ | ✓ | — |
| Next/prev note (←/→) | ✓ | ✓ | — |

### Advanced (Out of Scope for MVP)
| Feature | MuseScore | HarmonyForge |
|---------|-----------|--------------|
| Piano roll editor | ✓ | — |
| MIDI keyboard input | ✓ | — |
| Lyrics entry | ✓ | — |
| Rehearsal marks | ✓ | — |
| Magnetic layout | ✓ | — |
| Real-time collaboration | Flat | — |

---

## Keyboard Shortcuts (HarmonyForge)

| Key | Action |
|-----|--------|
| N | Toggle draw mode |
| Esc | Exit draw mode |
| ↑ | Pitch up semitone |
| ↓ | Pitch down semitone |
| ⌘↑ / Ctrl+↑ | Pitch up octave |
| ⌘↓ / Ctrl+↓ | Pitch down octave |
| 1 | Whole note |
| 2 | Half note |
| 3 | Quarter note |
| 4 | Eighth note |
| 5 | 16th note |
| 6 | 32nd note |
| ⌘Z | Undo |
| ⇧⌘Z | Redo |
| ⌘C | Copy |
| ⌘X | Cut |
| ⌘V | Paste |
| Delete / Backspace | Delete selected |
