
class SelectorsGeneration:
    """Selectors generation functions
    Trying to generate selectors like Firefox or maybe cleaner ones!? Ehm
    Inspiration: https://searchfox.org/mozilla-central/source/devtools/shared/inspector/css-logic.js#591"""

    def __general_selection(self, selection: str = 'css') -> str:
        """Generate a selector for the current element.
        :return: A string of the generated selector.
        """
        selectorPath = []
        target = self
        css = selection.lower() == 'css'
        while target is not None:
            if target.parent:
                if target.attrib.get('id'):
                    # id is enough
                    part = (
                        f'#{target.attrib["id"]}' if css
                        else f"[@id='{target.attrib['id']}']"
                    )
                    selectorPath.append(part)
                    return (
                        " > ".join(reversed(selectorPath)) if css
                        else '//*' + "/".join(reversed(selectorPath))
                    )
                else:
                    part = f'{target.tag}'
                    # We won't use classes anymore because I some websites share exact classes between elements
                    # classes = target.attrib.get('class', '').split()
                    # if classes and css:
                    #     part += f".{'.'.join(classes)}"
                    # else:
                    counter = {}
                    for child in target.parent.children:
                        counter.setdefault(child.tag, 0)
                        counter[child.tag] += 1
                        if child._root == target._root:
                            break

                    if counter[target.tag] > 1:
                        part += (
                            f":nth-of-type({counter[target.tag]})" if css
                            else f"[{counter[target.tag]}]"
                        )

                selectorPath.append(part)
                target = target.parent
                if target is None or target.tag == 'html':
                    return (
                        " > ".join(reversed(selectorPath)) if css
                        else '//' + "/".join(reversed(selectorPath))
                    )
            else:
                break

        return (
            " > ".join(reversed(selectorPath)) if css
            else '//' + "/".join(reversed(selectorPath))
        )

    @property
    def css_selector(self) -> str:
        """Generate a CSS selector for the current element
        :return: A string of the generated selector.
        """
        return self.__general_selection()

    @property
    def xpath_selector(self) -> str:
        """Generate a XPath selector for the current element
        :return: A string of the generated selector.
        """
        return self.__general_selection('xpath')
