#!/bin/bash

echo "Pruning git branches, removing any local branches that have been deleted on the remote."
echo ""

echo "Fetching changes..."
git fetch -p

echo ""
echo "Remove local branches that do not exist on the remote."

for branch in $(git for-each-ref --format '%(refname) %(upstream:track)' refs/heads | awk '$2 == "[gone]" {sub("refs/heads/", "", $1); print $1}'); do
    echo "Deleting branch: $branch"
    git branch -D $branch

    if [[ $? -ne 0 ]]; then
        echo "[ERROR] Failed to remove branch '${branch}'"
    fi
done

echo "Done."
exit $?
