
cd ~/Desktop/CA_Project

echo "===== SUBMODULE CONFIGURATION ====="
if [ -f .gitmodules ]; then
    cat .gitmodules
else
    echo "No .gitmodules file found"
fi

echo "===== GIT IGNORE ====="
cat .gitignore

echo "===== REMOTE REPOSITORY ====="
git remote -v

echo "===== SUBMODULE STATUS ====="
git submodule status

echo "===== WORKING TREE ====="
git status

