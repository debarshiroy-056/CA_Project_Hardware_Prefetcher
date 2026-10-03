#!/bin/bash
set -e

python3 - <<'PY'
from pathlib import Path

p = Path("ChampSim/README.md")
text = p.read_text()

start = text.index("# Download dependencies")
end = text.index("# Compile", start)

section = r"""# Download dependencies

ChampSim uses [vcpkg](https://vcpkg.io) to manage its dependencies. The vcpkg checkout is not included in this repository. Before building, obtain vcpkg from its official repository and place it in the `vcpkg/` directory:

```bash
git clone https://github.com/microsoft/vcpkg.git vcpkg
./vcpkg/bootstrap-vcpkg.sh
./vcpkg/vcpkg install
```

"""

p.write_text(text[:start] + section + text[end:])
print("Dependency section replaced.")
PY

git add ChampSim/README.md
sed -n '18,28p' ChampSim/README.md