#%%
#google/language_v1-analyze_syntax
from google.cloud import language_v1


def sample_analyze_syntax(text_content):
    """
    Analyzing Syntax in a String

    Args:
      text_content The text content to analyze
    """

    client = language_v1.LanguageServiceClient()

    # text_content = 'This is a short sentence.'

    # Available types: PLAIN_TEXT, HTML
    type_ = language_v1.Document.Type.PLAIN_TEXT

    # Optional. If not specified, the language is automatically detected.
    # For list of supported languages:
    # https://cloud.google.com/natural-language/docs/languages
    language = "en"
    document = {"content": text_content, "type_": type_, "language": language}

    # Available values: NONE, UTF8, UTF16, UTF32
    encoding_type = language_v1.EncodingType.UTF8

    response = client.analyze_syntax(
        request={"document": document, "encoding_type": encoding_type}
    )
    # Loop through tokens returned from the API
    for token in response.tokens:
        # Get the text content of this token. Usually a word or punctuation.
        text = token.text
        print("Token text: {}".format(text.content))
        print(
            "Location of this token in overall document: {}".format(text.begin_offset)
        )
        # Get the part of speech information for this token.
        # Part of speech is defined in:
        # http://www.lrec-conf.org/proceedings/lrec2012/pdf/274_Paper.pdf
        part_of_speech = token.part_of_speech
        # Get the tag, e.g. NOUN, ADJ for Adjective, et al.
        print(
            "Part of Speech tag: {}".format(
                language_v1.PartOfSpeech.Tag(part_of_speech.tag).name
            )
        )
        # Get the voice, e.g. ACTIVE or PASSIVE
        print(
            "Voice: {}".format(
                language_v1.PartOfSpeech.Voice(part_of_speech.voice).name
            )
        )
        # Get the tense, e.g. PAST, FUTURE, PRESENT, et al.
        print(
            "Tense: {}".format(
                language_v1.PartOfSpeech.Tense(part_of_speech.tense).name
            )
        )
        # See API reference for additional Part of Speech information available
        # Get the lemma of the token. Wikipedia lemma description
        # https://en.wikipedia.org/wiki/Lemma_(morphology)
        print("Lemma: {}".format(token.lemma))
        # Get the dependency tree parse information for this token.
        # For more information on dependency labels:
        # http://www.aclweb.org/anthology/P13-2017
        dependency_edge = token.dependency_edge
        print("Head token index: {}".format(dependency_edge.head_token_index))
        print(
            "Label: {}".format(
                language_v1.DependencyEdge.Label(dependency_edge.label).name
            )
        )

    # Get the language of the text, which will be the same as
    # the language specified in the request or, if not specified,
    # the automatically-detected language.
    print("Language of the text: {}".format(response.language))
# %%
sample_analyze_syntax('''
The cat is eating its food
''')
# %%
