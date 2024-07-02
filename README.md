# TextProcessingModule
**Background**: This module was developed during an internship at **Deutsche Museum Nürnberg (Zukunftsmuseum)** 
as a protective prompt filtering mechanism for a possible interactive installation featuring 
an image generation pipeline from speech to image. It was designed to **process english language** (see [Multilingualism]).

The **TextProcessingModule** has two **submodules**:
1. **ToxicityFilter**: Provides the ToxicityFilter, a two-tiered approach to **filter texts containing toxic language**, and a SpanDetector which can return the span or characters of toxic parts in a text.
2. **KeywordExtractor**: It provides keyword extraction with **tagging** and **HTML highlighting** functionality.  

> [!WARNING]
> The word lists in `TextProcessingModule` and the examples used in the `DEMO_*.ipynb` files contain **offensive langauge**, so be aware of that.

> [!NOTE] 
> As a first filter stage `ToxicityFilter` uses **word lists**. These lists **should be reviewed and maybe manually adapted** since they are not extensive. They might be too rigorous or not rigorous enough for a given purpose.
> They can be found in the **TextProcessingModule** folder.

> [!NOTE]
> When the second filter stage (detoxify) is applied, it uses a **default threshold** for the input texts toxicity of 0.5.
> Please experiment and dial in this value.

---
## Installation
- Download the `requirements.txt` file to your desired working directory.
- In your working directory:
    - [optional] Create a virtual environment: `python -m venv venv`
    - [optional] Run `source venv/bin/activate` to activate the environment)
    - Install the required packages: `pip install -r requirements.txt`

[verify!] Alternatively, if you use conda, you can use a pre-configured virtual conda environment. To install it:
- Download the `tpm-venv_scratch.yml` file into your working directory
- In your working directory run:
```bash
conda env create -p ./tpm-venv -f ./tpm-venv_scratch.yml
```
to create a new conda environment named `tpm-venv` inside your working directory or

```bash
conda env create -n tpm-venv -f ./tpm-venv_scratch.yml
```

to create it in condas standard location for environments.


- Finally: Download the `TextProcessingModule` folder into your working directory

Now you can import it like any python module inside your working directory.

To try out TextProcessingModule you can download our **Jupyter Notebook demo** `DEMO_TextProcessingModule.ipynb` to your working directory.
This requires **jupyter-notebook or jupyter-lab** to be installed (e.g. via `pip install jupyterlab`) or an IDE that supports jupyter-notebooks.
You might also want to run `pip install ipywidgets` to circumvent any error messages regarding `tqdm`. 

---



## Usage:
TextProcessingModule provides **toxicity filtering**, **toxic span detection** and **keyword extraction**.
See the `DEMO_ToxicityFilter.ipynb`, `DEMO_ToxicSpanDetection.ipynb` and `DEMO_KeywordExtraction.ipynb` for **comprehensive usage examples**.
> They can be viewed within GitHub. However, if you want to use and execute them locally, [Jupyter](https://jupyter.org/install) must be installed or your IDE must support jupyter notebooks.
---

## Explanation
### Toxicity Filter
`TextProcessingModule.toxicity_filter` provides the ToxicityFilter class. ToxicityFilter uses a two-tiered filter approach:

1. Strictly **filtering** prompts **by basic lists** of vulgar or swear words, immediately neglecting the input text.
2. **Detecting** more subtle forms of problematic textual information like **threats, obscenity, insults, and identity-based hate** using [detoxify](https://github.com/unitaryai/detoxify) if the first filter stage was passed. A **threshold** (range [0; 1]) can be used to sharpen the filter.

Detoxify rates a prompt in five different categories and assigns a probability to them. ToxicityFilter takes the highest probability and compares it to the threshold. If the threshold is exceeded, a **WARNING string** is returned.


> [!NOTE]
> The texts are tokenized but not lemmatized prior applying the word list filter. This will be a future improvement.

> [!NOTE]
> The two filter stages can also be used **separately**. See `DEMO_ToxicityFilter.ipynb`.

> [!NOTE]
> ToxicityFilter can be initialized with **three different models**: 'original' (default), 'unbiased', 'multilingual'.
> The model names are passed down to [detoxify](https://github.com/unitaryai/detoxify); see their documentation for **model explanation**. 


### Span Detection
The `toxicity_filter` submodule also provides a class `SpanDetector`.
It can return the **character span of toxic parts** of a text. 
It also provides **additional functionality** for returning the input text:
- **Sanitize the input**, i.e. replacing toxic characters with a custom character (default: '*').
- **Tag the input** with a custom tag.
- **HTML highlighting** of toxic spans.

> [!NOTE]
> See `DEMO_ToxicSpanDetection.ipynb` for usage examples.

### Keyword Extraction
`TextProcessingModule.keyword_extraction` provides the `KWExtractor` class.
It uses [yake](https://github.com/LIAAD/yake) for extraction and provides additional **custom tagging** and **HTML highlighting** as well.

It was thought to help the speech to text pipeline reduce spoken input to meaningful words for the image generation prompt.

---
## Multilingualism
> [!NOTE]
> The speech to image pipeline this module was designed for, would translate speech into english text as an image
> generation prompt. Thus, the module was **tailored to English**.
> Although technically some of the dependencies in use provide **multilingualism** to some extent, you would need
> to provide your own wordlists and the code would need further improvement to support the dependencies' multilingualism.

---
## Attributions
- **Tokenization** of texts prior applying the word list filter is done using **SoMaJo** (see: https://github.com/tsproisl/SoMaJo)
- The **word list** for span detection was taken from [erikdyan/toxic_span_detection](https://github.com/erikdyan/toxic_span_detection/blob/981c7f2d7fba6625a7cb57678d80ef0341b3288b/data/wordlist.txt)
- The second filter stage (toxicity classification) uses [detoxify](https://github.com/unitaryai/detoxify)
- For **keyword extraction** [yake](https://github.com/LIAAD/yake) is used.
- For **toxic span detection** [mudes](https://pypi.org/project/mudes/) is used.
