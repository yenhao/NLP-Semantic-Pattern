# NLP-Semantic-Pattern

The propose of this work is to get the possible pattern for normal English using by analyzing a bunch of sentence.
For example, 
previous we can only get experience in something
Currently, we can get experience in act (44.3%)|artifical (15.8%) 

We are trying to make the phrase/ grammer more precise. We will talk about the process in below chapter.

#WriteAHead

Generate the new pattern with possibility!

1.Go to writeahead folder.

2.Run 'cat citeseerx.difficulty.txt (or citeseerx) | python re.pat.map.py | sort | python re.pat.generate.py' to generate the new pattern with possibility.

In re.pat.maper.py, it convert the original sentence into format: headword:postag<tab>pattern<tab>collocation<tab>sentence .

In re.pat.generate.py, it disambiguate the word and get the possible category for each pattern. Then reassemble it into  a new pattern.

3.Run 'cat citeseerx.difficulty.txt (or citeseerx) | ../lmr 8m 8 'python re.pat.map.py' 'python re.pat.filter.py | python re.pat.reduce.py' writeahead_result' to get the corresponding sentence to combine them to be our result.


It can make a little modify to become map reduce structure, but I was lazy, lol.

#linggle

Because linggle have larger scale data than writeahead, we believe that if we utilizing linggle's dataset the result will be more robust.

1.Go to linggle folder.

2.Run 'cat linggle_pattern.txt | ../lmr 8m 8 'python linggle.pat.map.py' 'python linggle.pat.reduce.py' linggle_result' to get the format: pattern <tab> new_pattern.

linggle_pattern is using the pattern (ex: experience in something) of writeAhead to query the linggle, then get the colls for each pattern.

3.Run 'cat citeseerx | ../lmr 8m 8 'python ../writeahead/re.pat.map.py' 'python linggle_sen_generate.py' linngle_sen_result' to get the corresponding sentence to combine them to be our result.





