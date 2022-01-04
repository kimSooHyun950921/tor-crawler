import cssselect

class AdRemover(object):
    """
    This class applies elemhide rules from AdBlock Plus to an lxml
    document or element object. One or more AdBlock Plus filter
    subscription files must be provided.

    Example usage:

    >>> import lxml.html
    >>> remover = AdRemover('fanboy-annoyance.txt')
    >>> doc = lxml.html.document_fromstring("<html>...</html>")
    >>> remover.remove_ads(doc)
    """

    def __init__(self, *rules_files):
        if not rules_files:
            raise ValueError("one or more rules_files required")

        translator = cssselect.HTMLTranslator()
        rules = []

        for rules_file in rules_files:
            with open(rules_file, 'r') as f:
                for line in f:
                    # elemhide rules are prefixed by ## in the adblock filter syntax
                    if line[:2] == '##':
                        try:
                            rules.append(translator.css_to_xpath(line[2:]))
                        except cssselect.SelectorError:
                            # just skip bad selectors
                            pass

        # create one large query by joining them the xpath | (or) operator
        self.xpath_query = '|'.join(rules)


    def remove_ads(self, tree):
        """Remove ads from an lxml document or element object.

        The object passed to this method will be modified in place."""

        for elem in tree.xpath(self.xpath_query):
            print(elem)
            elem.getparent().remove(elem)