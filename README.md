# mg-lc-parse
A basic left-corner parser for minimalist grammars, implemented in Python.
The parsing algorithm is based on the following [paper](https://aclanthology.org/W18-2809/).

## Usage

---
### Basic Run
The main function is `parse`, given in the module `lc_parser.py`. 
It takes an input sentence (list of words) and returns a list of all possible parses. 
Each parse is a final, successful configuration the parser has reached, alongside the history of applied rules.

Here is a basic template for using the parser:
```python
g1 = MG('input/g1.json')
parser = LCParser(g1)
results = parser.parse(['Aca', 'knows', 'what', 'Bibi', 'likes'])
```

#### General flow
1. Load the grammar from a JSON file.
2. Create a parser object with the loaded grammar.
3. Parse a sentence:
   1. Create a stack with the initial config.
   2. while (stack != empty):
      1. Pop a configuration from the stack.
      2. Apply all possible rules to the configuration.
      3. If the rule produced a result, create a new configuration and push it to the stack.
      4. If the configuration is successful, add it to the results list.

### Grammar Rules
Note that the default parsing behaviour is loading the rules from the grammar.
Regarding _empty-shift_ rules (where the shifted lexical item is not consumed from the remaining input): 
for each empty lexical item in the grammar (`'': ["=v,c", "=v,+wh,c"]`), the appropriate _empty-shift_ rules 
are created and added to the parsing rules list.

Another working assumption is that _shift_ rules are never executed consecutively.
That is, if a _shift_ rule is applied, the next rule cannot be another _shift_ rule, and
is therefore skipped with the current log:\
`Skipping rule: {rule} because it follows a shift rule!`

### Parsing Modes
The `parse` function supports two more modes of running:
1. `rules`: A list of rules to be used in the parsing process. This replaces the default list of rules loaded from the grammar.
2. `manual`: If set to true, alongside a list of rules, the parser will apply them in the order given (for directly testing the correct parsing process).

In either case, when a rule's condition is not met, or we tried to apply it and got nothing new (it's result will be `None`),
we can except a log message ending in `returning same config`. 

### Other
- Current use of log levels are to show the parsing process in detail and display with color (that's why rule application are logged as "warnings")

### Credits
- Based on the original implementation in prolog by [Miloš Stanojević](https://github.com/stanojevic/Left-Corner-MG-parser).
