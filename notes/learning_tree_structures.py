paths = [".codex",
".gitignore",
"TODO.md",
"cherry-files-diff.sh",
"main.py",
"modules/__init__.py",
"modules/cherry_files_diff.py",
"my_app.tcss",
"notes/cherry-files-toolkit.md",
"notes/learning-bash.md",
"references/cherry-files-diff.sh",
"references/ref.py",
"ui-ux/cherry-files-toolkit.excalidraw",
"ui-ux/cherry-toolkit-design-01.png",
"ui-ux/cherry-toolkit-design-02.png",
"ui-ux/lazygit-reference.png",
"utilities/__init__.py",
"utilities/git_functions.py",
"widgets/__init__.py",
"widgets/filterable_option_picker.py",
"test1/test2/test3/hello_world_1.txt",
"test4/test5/test6/hello_world_2.txt"]


def build_tree(paths):
    tree = {}
    for path in paths:
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"📂 PATH      : {path}")
        parts = path.split("/")
        print(f"✂️  PARTS     : {parts}")
        node = tree
        print(f"🌳 TREE SO FAR: {tree}")
        print()

        for i, part in enumerate(parts):
            indent = "   " * i  # indent deeper for each level
            print(f"{indent}👉 VISITING  : '{part}'")
            if part not in node:
                node[part] = {}
                print(f"{indent}✅ CREATED   : '{part}' (was missing)")
            else:
                print(f"{indent}⏭️  SKIPPED   : '{part}' (already exists)")
            node = node[part]
            print(f"{indent}📍 MOVED INTO: '{part}' → node is now {node}")
            print()

    return tree


tree = build_tree(paths)
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("✅ FINAL TREE:")
print(tree)
