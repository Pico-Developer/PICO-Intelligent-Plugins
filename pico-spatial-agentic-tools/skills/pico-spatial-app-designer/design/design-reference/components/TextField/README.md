# TextField

A single-line text input, 280 wide by default and at least 48 high, radius 12 (`radiusMediumLarge`).

## Layout
- Fill `fillTertiary`; while focused `fillSecondary`. Text `bodyLarge` in `labelPrimary`; placeholder `labelQuaternary` (30% of that alpha while focused).
- Left padding 12 (44 with a leading icon: 8 + 32 box + 4). Text sits in 12 vertical padding. Right side: a clear button (40x40, a round x glyph, shown when focused and not empty) after 12 start padding and 4 end padding; or your trailing content in a 40x40 minimum box with 4 padding; or a 12dp spacer.
- Error: a 1dp border drawn inside in `error`; the supporting text turns `error`. Supporting text is `bodySmall` (12/16) in `labelTertiary`, 4 below the field.
- Pressed draws `lightenPressed` unless the field is focused. Disabled alpha 0.3. Hover is the native spatial hover effect on a PICO device, not a color; the web build draws the non-spatial fallback, 12% white. Pressed draws `lightenPressed` (12% white).

## When to use
- **Use for:** free text of one line: a name, a code, a title.
- **Don't use for:** a number with steps (use `NumberField` or `Stepper`), search (use `SearchField`), multi-line notes (use `TextArea`), a fixed set of choices (use `Option` or a `Menu`).
- **Alternatives:** `TextArea`, `SearchField`, `NumberField`.
- **Do:** keep a visible field name above or beside the input, including after a value is entered. Use the placeholder for an example and supporting text for the rule. State what failed and how to correct it in the error message.
- **Don't:** use the placeholder as the only label or show validation errors on an untouched field before submission. A required field can report an empty value after submission.

## Complete field composition

- The SDK TextField provides the input, placeholder, supporting text and error appearance. Compose the persistent field name in the parent layout; the caller owns validation. A visible name is not a new native `label` parameter.
- The preview uses **Device name (required)** as the persistent name, **For example: Living Room Headset** as the placeholder, and **Required, up to 20 characters.** as the normal supporting text. These are example application rules, not SDK defaults. Validation trims leading/trailing whitespace and counts Unicode code points; whitespace-only input is empty.
- Report an empty name as **Enter a device name.**, and an overlong name as **Device name cannot exceed 20 characters.** Keep the field name visible in both cases. Avoid generic messages such as `Invalid value`.
- The interactive example validates on the first submission, then revalidates on each edit and clears the error as soon as the value is valid. Button activation and Enter both submit; IME confirmation does not submit during composition. Its success message reports validation only; nothing is saved.
- Label the fixed error sample **Error state example** and explain that its state is static. It demonstrates error appearance rather than initial validation behavior.
- The Web preview associates the visible name with the actual shadow input via `aria-label`, links its supporting text with `aria-describedby`, and synchronizes `aria-invalid`. This wiring is local to the example; the shared runtime does not currently provide it automatically. An outer HTML `label for` pointing at the custom element is insufficient to label its shadow input.

## Web API
- `<sui-text-field>` attributes: `value`, `placeholder`, `supporting-text`, `error`, `disabled`, `readonly`, `clearable` (default on, `clearable="false"` removes it), `width` (default 280), `container-color`, `text-color`, `placeholder-color`, `focus-color`, `supporting-color`. Slots: `leading`, `trailing`, `supporting`. Property `value` reads the text.
- Events: `value-change` (`detail.value`).

## Preview and shared rules

[Open this family’s preview](preview.html). The first section retains the empty, filled, error and leading-icon variants with SDK-default input appearance, adding persistent names and concrete supporting text. The leading icon uses the local headset resource for the device-name example. The added complete-field section is labelled as a Plan recommendation; its caller-owned layout uses a 280px width, an 8px label gap and 16px between the field, action and status. See [general rules](../../general-rules.md), [local icons](../../assets/icons/README.md), and [browser/native limitations](../../runtime/README.md#browsernative-differences).
