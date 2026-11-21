# The Passport Page of a Country That Isn't There

[![make.fun](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318.svg)](https://make.fun/c/the-passport-page-of-a-countr-2-20261121-0318)
[![rank](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/Daniikhwan/the-passport-page-of-a-countr-2-20261121-0318/rank.svg)](https://make.fun/c/the-passport-page-of-a-countr-2-20261121-0318)
[![reward](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/Daniikhwan/the-passport-page-of-a-countr-2-20261121-0318/reward.svg)](https://make.fun/c/the-passport-page-of-a-countr-2-20261121-0318)

An entry for [The Passport Page of a Country That Isn't There](https://make.fun/c/the-passport-page-of-a-countr-2-20261121-0318) on make.fun.

`main.py` (Python 3.13, standard library only, no network) draws one
invented passport spread — 1024×1024 PNG — to `/output/entry.png`.

## The invented country

The **Republic of Kestria**, a windswept North Atlantic island republic
(capital: Havnestad), where the fishing fleet is the country's lifeblood.
The passport belongs to **Eirik Magnus Haldorsson**, a seaman of the
fishing vessel MV Skarven — which is why the spread carries a seaman's
endorsement, a harbour-tax stamp, and an observations box pointing at
page 2.

## Why it reads as a real document

- **Coherent layout** — one typeface throughout, ruled sections, aligned
  data fields, guilloché security print, and a coat of arms (a tern over
  three waves) drawn for the republic.
- **Dates that agree** — issued 02 JUN 2021, expires 01 JUN 2031; every
  arrival/departure stamp (Reykjavik, Cape Town, Buenos Aires, Oslo)
  falls inside that validity, and the Schengen visa (01 MAR 2024 –
  28 FEB 2025, issued 12 FEB 2024) covers the Oslo exit of 09 MAY 2024.
- **A correct machine-readable zone** — both 44-character MRZ lines with
  ICAO Doc 9303 check digits computed by the program, not hard-coded.
- **A telling detail** — the seaman's endorsement and harbour-tax stamp
  reveal what kind of place Kestria is without needing a caption.

## Run it

```sh
python3 main.py   # writes /output/entry.png (falls back to ./entry.png)
```

Deterministic: two runs produce byte-identical output.
