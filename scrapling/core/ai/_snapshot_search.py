from scrapling.core._types import List, Pattern, Tuple


def _search_snapshot(snapshot: str, pattern: Pattern[str]) -> str:
    """Keep matching lines, nearby context and ancestor paths without changing refs."""
    lines = snapshot.split("\n") if snapshot else []
    matches = [index for index, line in enumerate(lines) if pattern.search(line)]
    if not matches:
        return ""
    retained = {nearby for index in matches for nearby in range(max(0, index - 3), min(len(lines), index + 4))}
    ancestors: List[Tuple[int, int]] = []
    for index, line in enumerate(lines):
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip())
        while ancestors and ancestors[-1][0] >= indent:
            ancestors.pop()
        if index in retained:
            retained.update(parent for _, parent in ancestors)
        ancestors.append((indent, index))
    output: List[str] = []
    previous = -1
    for index in sorted(retained):
        if index > previous + 1:
            output.append("...")
        output.append(lines[index])
        previous = index
    if previous < len(lines) - 1:
        output.append("...")
    return "\n".join(output)
