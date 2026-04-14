---
paths:
  - "**/*.css"
  - "**/*.scss"
  - "**/*.module.css"
  - "**/*.module.scss"
---

# CSS & Design Token Rules

## Tinted Grey System (Non-negotiable)
Pure achromatic greys (Saturation 0%) are prohibited. All greys must be Tinted Greys with a subtle mix of the PRIMARY color Hue.

HSB curve: PRIMARY Hue fixed, lighter = lower S (1~2%), darker = higher S (8~12%).
- Gray 50: B=98~99%, S=1~2%
- Gray 100~300: B=85~97%, S=2~3%
- Gray 400~600: B=40~70%, S=4~6%
- Gray 700~800: B=20~35%, S=6~8%
- Gray 900: B=10~15%, S=8~12%

## Prohibited Values
- `#000000`, `#333333` and other pure achromatic colors: prohibited
- S=0% greys: prohibited
- Implementation agents hardcoding grey values: prohibited

## Rules
- `!important`: prohibited
- All colors must use design tokens / CSS variables (hardcoded hex prohibited)
- Korean comments required
