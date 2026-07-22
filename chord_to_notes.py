import traceback
import re
from chord_yacc import parser
import readline

roots = {
    "C": 0,
    "D": 2,
    "E": 4,
    "F": 5,
    "G": 7,
    "A": 9,
    "B": 11,
}

scale_templates = dict(
    major={0, 2, 4, 5, 7, 9, 11},
    whole_tone={0, 2, 4, 6, 8, 10},
    aeolian={0, 2, 3, 5, 7, 8, 10},
    dorian={0, 2, 3, 5, 7, 9, 10},
    phrygian={0, 1, 3, 5, 7, 8, 10},
    lydian={0, 2, 4, 6, 7, 9, 11},
    lydian_minor={0, 2, 4, 6, 7, 8, 10},
    mixolydian={0, 2, 4, 5, 7, 9, 10},
    locrian={0, 1, 3, 5, 6, 8, 10},
    harmonic_minor={0, 2, 3, 5, 7, 8, 11},
    melodic_minor_ascending={0, 2, 3, 5, 7, 9, 11},
    melodic_minor_descending={0, 2, 3, 5, 7, 8, 10},
    minor_blues={0, 3, 5, 6, 7, 10},
    major_blues={0, 2, 3, 4, 7, 9},
    neapolitan_minor={0, 1, 3, 5, 7, 8, 11},
    neapolitan_major={0, 1, 3, 5, 7, 9, 11},
    whole_half_diminished={0, 2, 3, 5, 6, 8, 9, 11},
    half_whole_diminished={0, 1, 3, 4, 6, 7, 9, 10},
    enigmatic={0, 1, 4, 6, 8, 10, 11},
    altered={0, 1, 3, 4, 6, 8, 10},
)

DEBUG = False


def get_pitch_value(pitch: str) -> int:
    match pitch:
        case "#":
            return 1
        case "##":
            return 2
        case "b":
            return -1
        case "bb":
            return -2
        case _:
            return 0


def get_notes_from_quality(root_value: int, quality: str) -> list[tuple[int, str]]:
    match quality:
        case "m":
            return [(root_value + 3, "b3"), (root_value + 7, "5")]
        case "M":
            return [(root_value + 4, "3"), (root_value + 7, "5")]
        case "aug":
            return [(root_value + 4, "3"), (root_value + 8, "#5")]
        case "dim":
            return [(root_value + 3, "b3"), (root_value + 6, "b5")]
        case "ø":
            return [
                (root_value + 3, "b3"),
                (root_value + 6, "b5"),
                (root_value + 10, "b7"),
            ]
        case _:
            raise ValueError(f"Type of quality not found '{quality}'.")


def get_notes_from_elements(root_value: int, elements: list, quality: str):
    values_to_add = {}
    values_to_remove = set()
    for element in elements:
        if isinstance(element, tuple):
            match element[0]:
                case "sus":
                    handle_sus(element[1], root_value, values_to_add, values_to_remove)
                case "add":
                    handle_add(element[1], root_value, values_to_add)
                case "no":
                    handle_omission(element[1], root_value, values_to_remove)
                case "set":
                    for set_element in element[1]:
                        if set_element.startswith("no"):
                            handle_omission(
                                set_element[2:], root_value, values_to_remove
                            )
                        elif set_element.startswith("add"):
                            handle_add(set_element[3:], root_value, values_to_add)
                        elif set_element.startswith("M"):
                            handle_major(set_element[1:], root_value, values_to_add)
                        else:
                            handle_set_pitch_number(
                                root_value,
                                set_element,
                                values_to_add,
                                values_to_remove,
                                quality,
                            )
                case "M":
                    handle_major(element[1], root_value, values_to_add)
                case "number":
                    handle_number(
                        element[1], root_value, values_to_add, values_to_remove, quality
                    )
                case "pitch_number":
                    handle_pitch_number(
                        element[1], root_value, values_to_add, values_to_remove, quality
                    )
                case _:
                    raise ValueError(f"Type of element not found '{element[0]}'.")
        elif isinstance(element, str):
            match element:
                case "6/9":
                    values_to_add[root_value + 9] = "6"
                    values_to_add[root_value + 14] = "9"
                case _:
                    raise ValueError("Type of element not found.")

    return values_to_add, values_to_remove


def handle_pitch_number(
    element: str,
    root_value: int,
    values_to_add: dict,
    values_to_remove: set,
    quality: str,
):
    if element.startswith("b"):
        number = element[1:]
        offset = -1
        prefix = "b"
    elif element.startswith("#"):
        number = element[1:]
        offset = 1
        prefix = "#"
    else:
        raise ValueError(f"Unknown type inside set '{element}'.")

    has_seventh = any(lbl in ["7", "M7", "dim7", "6"] for lbl in values_to_add.values())

    if quality == "ø":
        has_seventh = True

    if not has_seventh and number in ["9", "11", "13"]:
        seventh_label = "dim7" if quality == "dim" else "7"
        seventh_value = root_value + (9 if quality == "dim" else 10)
        values_to_add[seventh_value] = seventh_label

    match number:
        case "5":
            values_to_add[root_value + 7 + offset] = prefix + "5"
            values_to_add.pop(root_value + 7, None)
            values_to_remove.add(root_value + 7)
        case "9":
            values_to_add[root_value + 14 + offset] = prefix + "9"
            values_to_add.pop(root_value + 14, None)
            values_to_remove.add(root_value + 14)
        case "11":
            values_to_add[root_value + 17 + offset] = prefix + "11"
            values_to_add.pop(root_value + 17, None)
            values_to_remove.add(root_value + 17)
        case "13":
            values_to_add[root_value + 21 + offset] = prefix + "13"
            values_to_add.pop(root_value + 21, None)
            values_to_remove.add(root_value + 21)
        case _:
            raise ValueError(f"Unknown pitch number '{number}'.")


def handle_major(element: str, root_value: int, values_to_add: dict):
    match element:
        case "7":
            values_to_add[root_value + 11] = "M7"
        case "9":
            values_to_add[root_value + 11] = "M7"
            values_to_add[root_value + 14] = "9"
        case "11":
            values_to_add[root_value + 11] = "M7"
            values_to_add[root_value + 14] = "9"
            values_to_add[root_value + 17] = "11"
        case "13":
            values_to_add[root_value + 11] = "M7"
            values_to_add[root_value + 14] = "9"
            values_to_add[root_value + 17] = "11"
            values_to_add[root_value + 21] = "13"
        case _:
            raise ValueError(f"Type of Major not found '{element}'.")


def handle_number(
    element: str,
    root_value: int,
    values_to_add: dict,
    values_to_remove: set,
    quality: str,
):
    seventh_label = "dim7" if quality == "dim" else "7"
    match element:
        case "2":
            values_to_add[root_value + 2] = "2"
        case "5":
            values_to_remove.update([root_value + 4, root_value + 3])
            values_to_add[root_value + 7] = "5"
        case "6":
            values_to_add[root_value + 9] = "6"
        case "7":
            values_to_add[root_value + (9 if quality == "dim" else 10)] = seventh_label
        case "9":
            values_to_add[root_value + (9 if quality == "dim" else 10)] = seventh_label
            values_to_add[root_value + 14] = "9"
        case "11":
            values_to_add[root_value + (9 if quality == "dim" else 10)] = seventh_label
            values_to_add[root_value + 14] = "9"
            values_to_add[root_value + 17] = "11"
        case "13":
            values_to_add[root_value + (9 if quality == "dim" else 10)] = seventh_label
            values_to_add[root_value + 14] = "9"
            values_to_add[root_value + 17] = "11"
            values_to_add[root_value + 21] = "13"
        case _:
            raise ValueError(f"Invalid chord number '{element}'.")


def handle_set_pitch_number(
    root_value: int,
    element: str,
    values_to_add: dict,
    values_to_remove: set,
    quality: str,
):
    if element.startswith("b"):
        number = element[1:]
        handle_add(number, root_value - 1, values_to_add, label_override="b" + number)
    elif element.startswith("#"):
        number = element[1:]
        handle_add(number, root_value + 1, values_to_add, label_override="#" + number)
    elif element.isdigit():
        number = element
        handle_add(number, root_value, values_to_add)
        return
    else:
        raise ValueError(f"Unknown type inside set '{element}'.")

    match number:
        case "5":
            values_to_add.pop(root_value + 7, None)
            values_to_remove.add(root_value + 7)
        case "9":
            values_to_add.pop(root_value + 14, None)
            values_to_remove.add(root_value + 14)
        case "11":
            values_to_add.pop(root_value + 17, None)
            values_to_remove.add(root_value + 17)
        case "13":
            values_to_add.pop(root_value + 21, None)
            values_to_remove.add(root_value + 21)


def handle_sus(
    number: str, root_value: int, values_to_add: dict, values_to_remove: set
):
    values_to_remove.update([root_value + 4, root_value + 3])
    values_to_add.pop(root_value + 4, None)
    values_to_add.pop(root_value + 3, None)
    match number:
        case "2":
            values_to_add[root_value + 2] = "2"
        case "b2":
            values_to_add[root_value + 1] = "b2"
        case "4":
            values_to_add[root_value + 5] = "4"
        case "#4":
            values_to_add[root_value + 6] = "#4"
        case _:
            raise ValueError(f"Type of sus chord not found '{number}'.")


def handle_add(number: str, root_value: int, values_to_add: dict, label_override=None):
    match number:
        case "2":
            values_to_add[root_value + 2] = label_override or "2"
        case "4":
            values_to_add[root_value + 5] = label_override or "4"
        case "5":
            values_to_add[root_value + 7] = label_override or "5"
        case "6":
            values_to_add[root_value + 9] = label_override or "6"
        case "9":
            values_to_add[root_value + 14] = label_override or "9"
        case "11":
            values_to_add[root_value + 17] = label_override or "11"
        case "13":
            values_to_add[root_value + 21] = label_override or "13"
        case _:
            raise ValueError(f"Unknown 'add' value '{number}'.")


def handle_omission(number: str, root_value: int, values_to_remove: set):
    match number:
        case "3":
            values_to_remove.update([root_value + 4, root_value + 3])
        case "5":
            values_to_remove.add(root_value + 7)
        case _:
            raise ValueError(f"Type of omission not found '{number}'.")


def get_notes_from_inversion(
    root_value: int, inversion: tuple, result_set: set, labels: dict
):
    bass_note_name = inversion[1][0]
    bass_pitch = inversion[1][1:] if len(inversion[1]) > 1 else ""

    bass_val = roots[bass_note_name] + get_pitch_value(bass_pitch)
    bass_pc = bass_val % 12

    matched_value = None
    for val in result_set:
        if val % 12 == bass_pc:
            matched_value = val
            break

    if matched_value is not None:
        if matched_value == root_value:
            return result_set
        result_set.remove(matched_value)
        old_label = labels.pop(matched_value, None)

        min_val = min(result_set) if result_set else root_value
        new_bass = bass_pc
        while new_bass >= min_val:
            new_bass -= 12
        result_set.add(new_bass)
        if old_label is not None:
            labels[new_bass] = old_label
        return result_set

    min_val = min(result_set) if result_set else root_value
    new_bass = bass_pc
    while new_bass >= min_val:
        new_bass -= 12
    result_set.add(new_bass)
    labels[new_bass] = f"bass:{bass_note_name}"

    return result_set


def get_scale(root_value: int, result_set: set):
    aux_set = set([element % 12 for element in result_set])
    for key, value in scale_templates.items():
        normalized_scale = set([(element + root_value) % 12 for element in value])
        if aux_set.issubset(normalized_scale):
            if DEBUG:
                print(f"Transposed scale: {normalized_scale}; Result set: {result_set}")
            return key, set([element + root_value for element in value])
    return None


def get_spelled_note(val_mod: int, target_letter: str) -> str:
    base_val = roots[target_letter] % 12
    diff = (val_mod - base_val) % 12

    if diff > 6:
        diff -= 12

    if diff == 0:
        return target_letter
    elif diff > 0:
        return target_letter + ("#" * diff)
    else:
        return target_letter + ("b" * abs(diff))


def get_diatonic_step(label: str) -> int:
    match = re.search(r"\d+", label)
    if not match:
        return 1
    interval = int(match.group())
    return ((interval - 1) % 7) + 1


def spell_chord_tones(result_set: set, root_note: str, labels: dict) -> dict:
    alphabet = ["C", "D", "E", "F", "G", "A", "B"]
    root_idx = alphabet.index(root_note)
    spelled_chord = {}

    for val in result_set:
        val_mod = val % 12
        label = labels.get(val, "root")

        if label.startswith("bass:"):
            target_letter = label.split(":", 1)[1]
        else:
            step = get_diatonic_step(label)
            target_letter = alphabet[(root_idx + step - 1) % 7]

        spelled_chord[val] = get_spelled_note(val_mod, target_letter)

    return spelled_chord


def get_sorted_chord_notes(values: set, spelled_chord: dict) -> list[str]:
    aux = []
    for value in values:
        if value < 0:
            priority = -((value * -1) // 12)
        else:
            priority = value // 12

        if value in spelled_chord:
            note = spelled_chord[value]
        else:
            raise Exception(f"{value} not in spelled_chord")

        priority += value / 12
        aux.append((priority, note))

    aux.sort(key=lambda x: x[0])
    return [note for _, note in aux]


def get_notes(chord: tuple):
    root = chord[0]
    pitch = chord[1]
    quality = chord[2]
    elements = chord[3]
    inversion = chord[4]

    result_set = set()
    labels = {}

    root_value = roots[root] + get_pitch_value(pitch)
    result_set.add(root_value)
    labels[root_value] = "root"

    for value, label in get_notes_from_quality(root_value, quality):
        result_set.add(value)
        labels[value] = label

    values_to_add, values_to_remove = get_notes_from_elements(
        root_value, elements, quality
    )
    has_common_elements = bool(set(values_to_add) & values_to_remove)
    if has_common_elements:
        raise ValueError("Chord name is not constructed properly.")

    result_set.difference_update(values_to_remove)
    for removed_value in values_to_remove:
        labels.pop(removed_value, None)

    result_set.update(values_to_add.keys())
    labels.update(values_to_add)

    if inversion is not None:
        result_set = get_notes_from_inversion(root_value, inversion, result_set, labels)

    spelled_chord = spell_chord_tones(result_set, root, labels)

    scale = get_scale(root_value, result_set)
    scale_name = scale[0] if scale else "synthetic"

    chord_notes = get_sorted_chord_notes(result_set, spelled_chord)
    return chord_notes, scale_name


def main():
    print("Type a chord (e.g., Cmaj7, F#m7b5, G/D) or 'q' to quit")

    while True:
        parser.exito = True

        try:
            chord = input("\n > ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n  ~~")
            break

        if chord.lower() in ["q", "quit", "exit"]:
            print("  ~~")
            break
        if not chord:
            continue

        try:
            parsed_chord = parser.parse(chord)
            if not parser.exito or parsed_chord is None:
                print("  -> Invalid chord syntax")
                continue

            if DEBUG:
                print(f"After parsing: {parsed_chord}")

        except Exception as e:
            print(f"  -> Error parsing chord: {e}")
            if DEBUG:
                traceback.print_exc()
            continue

        try:
            chord_notes, scale_name = get_notes(parsed_chord)
            formatted_notes = " - ".join(chord_notes)
            display_scale = scale_name.replace("_", " ")
            print(f"   {formatted_notes}   [{display_scale}]")
        except Exception as e:
            print(f"  -> Error analyzing chord: {e}")
            if DEBUG:
                traceback.print_exc()


if __name__ == "__main__":
    main()
