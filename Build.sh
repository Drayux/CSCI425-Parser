echo "#!/bin/bash" > ZOBOS
echo "python3 zobos.py \$1 \$2" >> ZOBOS
chmod +x ZOBOS
source ~khellman/COMPGRADING/setup.sh ~khellman/COMPGRADING
