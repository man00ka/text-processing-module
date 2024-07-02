## IMPORT
from somajo import SoMaJo  #  State of the Art Web- and Social Media Tokenizer:
#  https://github.com/tsproisl/SoMaJo

from detoxify import Detoxify  #  toxicity classification:
#  https://github.com/unitaryai/detoxify
import pandas as pd
from mudes.app.mudes_app import MUDESApp  #  toxic-span-detection
#  https://pypi.org/project/mudes/

from yake.highlight import TextHighlighter


class ToxicityFilter:
    # todo: copy dockstring from below
    # TODO:
    #  - Use a language parameter in __init__() to pass 'de' or 'en'.
    #  - Choose 'en_PTB' or 'de_CMC' as the tokenizer language
    #  - and
    # TODO: Test if `device='mps'` works
    """Description:

    PARAMETERS:
    -----------
    'model' : str, default='original'
        String indicating the model to load. Options are: 'original',
        'unbiased', 'multilingual'. See https://github.com/unitaryai/detoxify
        for further details on the different models and their origin.

    'word_list' : str, default='default'
        Expects a file path to a text file containing custom filter words with
        one word per line.

    'kwargs': dict
        Pass additional arguments for detoxify (e.g. the device to use, i.e.
        cpu (default), cuda, etc.); see detoxify documentation (link above).
    """

    def __init__(self, model: str = 'original',
                 word_list: str = 'default',
                 keep_results: bool = False,
                 **kwargs):
        self.__FILTER_TRIGGERED = False  #
        self.__results = {'word_list_filter': {},
                          'detoxify_filter': {}}
        self.__keep_results = keep_results
        self.word_list_filter = WordListFilter(word_list=word_list, keep_results=keep_results)
        self.detoxify_filter = DetoxifyFilter(model=model, keep_results=keep_results, **kwargs)

    def set_keep_results(self, keep_results: bool):
        """This will make results persistent across multiple `apply()` calls by storing
        them in a dictionary
         {'word_list_filter': {input_text: result, ...},
          'detoxify_filter': {input_text: result, ...}}.

        However, keep in mind that the results contain the input text as dict
        keys, which might make the results dictionary grow quite large, depending
        on the amount of text that is processed."""
        self.__keep_results = keep_results
        self.word_list_filter.set_keep_results(True)
        self.detoxify_filter.set_keep_results(True)

    def get_results(self, as_dataframe: bool = False):
        if not as_dataframe:
            return self.__results
        if as_dataframe:
            # todo: check dataframe creation. bassd des?
            return pd.DataFrame.from_dict(self.__results)

    def apply(self, text: str, threshold=0.5, verbose=False) -> int | str:
        """
        Returns a WARNING string if problematic textual content
        is discovered or 'text' if not. It uses a two-tiered approach:
            (1) Strictly filtering prompts by basic lists of vulgar
                or swear words, immediately neglecting the input text.
            (2) Detecting more subtle forms of problematic textual
                information like threats, obscenity, insults, and
                identity-based hate using detoxify (https://github.com/unitaryai/detoxify)
                if the first filter stage was passed.
                The 'threshold' option can be used to sharpen the filter.
                Detoxify rates a prompt in five different categories
                and assigns a probability to them. The highest
                probability is taken and compared to the threshold.
                If 'threshold' is exceeded a WARNING string is returned.

        PARAMETERS:
            text : str
                The input prompt to apply the filter to
            threshold : float, defaults to 0.5
                Probability threshold between [0, 1] for the second stage of
                the filter (i.e. detoxify).
            verbose : boolean, False
                Set to True will make `apply()` return (1) the detected foul language token
                (word list filter) or (2) the detected likelihood of toxicity (detoxify filter).


        RETURNS:
            int | str : 1 if the filter triggered, 0 if none. A string if `verbose=True`.
        """

        # TODO:
        #  Lemmatization and separate filtering: Use lemmatized text for filtering
        #  by stop word lists and the original text for filtering with detoxify.

        if not self.__keep_results:
            # Reset results
            self.__results = {'word_list_filter': {},
                              'detoxify_filter': {}}

        # applying word list filter
        result = self.word_list_filter.apply(text, verbose=verbose)
        self.__add_to_results(result)
        if result is not None:
            return result
        else:
            # applying detoxify
            result = self.detoxify_filter.apply(text, threshold, verbose=verbose)
            self.__results["detoxify_filter"][text] = result
            return result

    def __add_to_results(self, result):
        # e.g. if the dict has two entries the idx will be 2 for the third entry,
        # so we follow 0-based indexing.
        idx = len(self.__results['word_list_filter'])
        self.__results['word_list_filter'][idx] = result


class SpanDetector:
    """e
    Identifies the character range of problematic content within
    the given String and can return list of character indices or
    a list of tuples each containing the range of a toxic span. 
    
    By default the 'en-large' model is loaded. However, it is
    possible to specify either of 'en-base', 'en-large',
    'multilingual-base', 'multilingual-large'.
    
    PARAMETERS:
    -----------
    'model_name_or_path' : str, (default = 'en-large')
    'model_type' : None
    'use_cuda' : Bool, (default = False)
    'cuda_device' : int (default = -1)
    """

    def __init__(self,
                 model_name_or_path='en-large',
                 model_type=None,
                 use_cuda=False,
                 cuda_device=-1, ):

        self.TSD = MUDESApp(model_name_or_path,
                            model_type,
                            use_cuda,
                            cuda_device)

    def detect(self, text, return_spans=True):
        """
        Returns a list of tuples with the range of toxic spans
        or a list of character indices when 'return_spans' is False.
        """
        return self.TSD.predict_toxic_spans(text,
                                            spans=return_spans)

    def return_toxic_token(self, text):
        toxic_spans = self.TSD.predict_toxic_spans(text, spans=True)
        return [text[span[0]:span[1] + 1] for span in toxic_spans]

    def tag_spans(self, text, tag="TOX"):
        """Returns the text with the detected spans sourrounded
        by the given tag which is "TOX" by default resulting in
        <TOX>...</TOX>.
        """
        toxic_token = self.return_toxic_token(text)

        th = TextHighlighter(max_ngram_size=3,
                             highlight_pre=f"<{tag}>",
                             highlight_post=f"</{tag}>")

        return th.highlight(text, toxic_token)

    def highlight_spans(self,
                        text,
                        color='lightblue'):
        """
        Returns the toxic spans sourrounded by HTML color style.
        Color can be either of 'lightblue', 'red' or 'gren or any
        hex color code like "#FFFFFF".
        """
        toxic_token = self.return_toxic_token(text)

        # Color Set:
        color_set = {"lightblue": '#217FF8',
                     "red": '#F94242',
                     "green": '#31C103'}

        if color in color_set.keys():
            color = color_set[color]
        else:
            color = color

        # Define TextHighlighter:
        th = TextHighlighter(max_ngram_size=3,
                             highlight_pre=f'<span style="color:{color}">',
                             highlight_post="</span>")
        return th.highlight(text, toxic_token)

    def replace_spans(self, text, char='*'):
        toxic_chars = self.TSD.predict_toxic_spans(text)
        return "".join(['*' if idx in toxic_chars else char for idx, char in enumerate(text)])


class WordListFilter:
    """Determine whether a given text contains a bad token.

    PARAMETERS:
    -----------
    'word_list' : str, defaults to a concatination of pre-defined word lists.
        You can specifiy the path to your own word list instead.
        Expects the word list to be a text file with one word per line.

    METHODS:
    --------
    'apply' : Apply the filter
    """

    def __init__(self,
                 word_list: str = 'default',
                 keep_results: bool = False,):
        self.__keep_results = keep_results
        self.__results = {}

        if word_list != 'default':
            # use custom word list
            with open(word_list) as f:
                self.word_list = f.read().strip().split("\n")
        elif word_list == 'default':
            # use pre-defined word lists
            with open("./TextProcessingModule/english_swear_words.txt") as f:
                swear_words = f.read().strip().split("\n")
            with open("./TextProcessingModule/english-vulgar-stop-words.txt") as f:
                vulgar_words = f.read().strip().split("\n")
            with open("./TextProcessingModule/tsd_wordlist.txt") as f:
                tsd_wordlist = f.read().strip().split("\n")
            self.word_list = swear_words + vulgar_words + tsd_wordlist

        self.tokenizer = SoMaJo(language="en_PTB", split_sentences=False)

    # Apply WordListFilter #
    def apply(self, text, verbose: bool = False):
        """
        Returns the first token that has a match in the word list, else
        None.
        """
        if not self.__keep_results:
            # Reset the results of previous runs
            self.__results = {}

        sentences = self.tokenizer.tokenize_text([text])
        sentence = [token.text for sentence in sentences for token in sentence]
        toxic_token = None
        for token in sentence:
            if token in self.word_list:
                toxic_token = token

        self.__results[text] = {"toxic_token": toxic_token}
        return self.__format_result(text, toxic_token, verbose=verbose)

        # TODO: Don't stop at first match. Instead find all matches and return
        #  a list of tuple with token and character indexes:
        #  [(token, [<chracter_indices>]), ...]

    def __format_result(self, text: str, token: str | None, verbose: bool = False):
        if token is None:
            return None
        if token is not None:
            if not verbose:
                return 1
            if verbose:
                return 1, {text: token}


    def get_results(self):
        return self.__results

    def set_keep_results(self, keep_results: bool):
        """This will make results persistent across multiple `apply()` calls by storing
        them in a dictionary {input_text: result}.

        However, keep in mind that the results contain the input text as keys,
        which might make the results dictionary grow quite large, depending
        on the amount of text processed."""
        self.__keep_results = keep_results


class DetoxifyFilter:
    """
    Detect more subtle forms of problematic textual
    information like threats, obscenity, insults, and 
    identity-based hate using detoxify (https://github.com/unitaryai/detoxify)
    Detoxify rates a prompt in five different categories
    and assigns a probability to them. When calling `apply` on this
    filter, the highest probability is taken and compared to the threshold.
    If 'threshold' is exceeded a WARNING string is returned.
    
    PARAMETERS:
    -----------
    'model' : str, 'original'
        String indicating the model to load. Options are: 'original',
        'unbiased', 'multilingual'. See https://github.com/unitaryai/detoxify
        for further details on the different models and their origin.
        

    METHODS:
    --------
    'apply' -> Returns str
    Returns a
    'get_scores' : Returns dict | pandas.DataFrame | None
        Returns a dict containing the results of the last call to  A pandas data frame with the different scores of the last application
        of the filter.
    
    'max_score' : tuple oder None
        A tuple of (<category>, <likelihood>) for the category with the
        highest likelihood of the last application of the filter.
        This could be used to filter by a probability threshold.


    METHODS:
    --------
    'apply' -> str
        Apply the filter.

    `get_scores` -> dict | pandas.DataFrame | None
        Returns the likelihood scores for overall toxicity and the different toxic
         classes like 'threat' or 'insult' etc. after `apply` was called.

    `get_toxicity` -> dict
        Returns only the overall toxicity after `apply` was called.

    """

    def __init__(self,
                 model='original',
                 keep_results: bool = False,
                 **kwargs):
        self.__keep_results = keep_results
        self.__model = Detoxify(model, **kwargs)
        self.__scores = {}
        self.__toxicity = {}

    def get_scores(self, as_dataframe: bool = False):
        if as_dataframe:
            return self.__make_dataframe(self.__scores)
        if not as_dataframe:
            return self.__scores

    def get_toxicity(self, as_dataframe: bool = False):
        if as_dataframe:
            return self.__make_dataframe(self.__toxicity)
        if not as_dataframe:
            return self.__toxicity

    def __make_dataframe(self, data: dict):
        values = data.values()
        index = list(data.keys())
        return pd.DataFrame(values, index=index).round(5)

    def set_keep_results(self, keep_scores: bool):
        """This will make results persistent across multiple `apply()` calls by storing
        them in a dictionary {input_text: result}.

        However, keep in mind that the results contain the input text as dict
        keys, which might make the results dictionary grow quite large, depending
        on the amount of text that is processed."""
        self.__keep_results = keep_scores

    def apply(self, text: str, threshold: float = 0.5, verbose: bool = False) -> int | str:
        """
        Returns 1 if the given text is classified as toxic and 0
        otherwise or a string if `verbose=True`.
        It can also store classification results which can be returned via
        `get_scores()` and `get_toxicity()`.
        
        PARAMETERS:
        -----------
        text : str
            The input text to apply the filter to
        threshold : float, defaults to 0.5
            `text` gets classified as toxic, if classification result (likelihood for toxicity)
            exceeds `threshold`.
        """
        if not self.__keep_results:
            # Reset the scores and toxicity
            self.__scores = {}
            self.__toxicity = {}

        prediction = self.__model.predict(text)
        self.__scores[text] = prediction

        toxicity = prediction['toxicity']
        self.__toxicity[text] = {"toxicity": toxicity}

        return self.__format_result(toxicity, threshold, verbose)

    def __format_result(self, toxicity: float, threshold: float, verbose: bool):
        if toxicity <= threshold:
            return None
        if toxicity > threshold:
            if not verbose:
                return 1
            if verbose:
                return 1, {"Detoxify: Toxicity above threshold!": {"Toxicity": toxicity, "Threshold": threshold}}
