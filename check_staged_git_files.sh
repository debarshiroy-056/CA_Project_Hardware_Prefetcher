cd ~/Desktop/CA_Project

echo "===== STAGED FILE COUNT ====="
git diff --cached --name-only | wc -l

echo "===== STAGED LARGE FILES ====="
git diff --cached --name-only -z | while IFS= read -r -d '' file; do
    if [ -f "$file" ]; then
        size=$(stat -f%z "$file")
        if [ "$size" -gt 100000000 ]; then
            echo "$size bytes: $file"
        fi
    fi
done

echo "===== STAGED DIRECTORY SUMMARY ====="
git diff --cached --name-only | cut -d/ -f1-2 | sort | uniq -c | sort -nr | head -25

echo "===== CURRENT STATUS ====="
git status --short
