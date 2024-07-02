import yake  # https://github.com/LIAAD/yake
from yake import KeywordExtractor
from yake.highlight import TextHighlighter
    

class KWExtractor:
    def __init__(self, lan: str='en', max_ngram_size: int=3, top_n: int=20, **kwargs):
        """
        More Keyword arguments to pass to the Keyword Extractor
        (see also https://github.com/LIAAD/yake for their purpose):
            {'dedupLim' : float, (default = 0.9),
            'dedupFunc' : str, (default = 'seqm'),
            'windowsSize' : int, (default = 1),
            'features'=None,
            'stopwords'=None}
        """
        self.extractor = KeywordExtractor(lan=lan, n=max_ngram_size, top=top_n, **kwargs)
        
    def extract(self, text: str):
        """
        Returns a list of tuples containing the keywords.
        """
        return self.extractor.extract_keywords(text)
    
    def tag(self, text: str, tag: str="kw"):
        keywords = self.extract(text)
        th = TextHighlighter(max_ngram_size = self.extractor.n,
                             highlight_pre = f"<{tag}>",
                             highlight_post= f"</{tag}>")
        return th.highlight(text, keywords)
    
    def highlight(self, text: str, color: str="lightblue"):
        """
        Returns the keyword spans sourrounded by HTML color style.
        
        PARAMETERS:
        -----------
        'color' : str, 'lightblue'
            Can also be 'red' or 'green' or a hex color 
            code like "#FFFFFF".
        """
        keywords = self.extract(text)
        
        # Color Set:
        color_set = {"lightblue":'#217FF8', 
                     "red":'#F94242',
                     "green":'#31C103'}
        if color in color_set.keys():
            color = color_set[color]
        else:
            color = color
            
        # Define TextHighlighter:
        th = TextHighlighter(max_ngram_size = self.extractor.n,
                             highlight_pre = f'<span style="color:{color}">',
                             highlight_post= "</span>")
        return th.highlight(text, keywords)
        