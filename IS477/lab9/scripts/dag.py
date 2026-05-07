rules = {}
rule_name, last_keyword = None, None
flag = True
keywords = ["input", "output", "script", "run", "shell", "notebook", "cwl", "params", "log", "wildcard_constraints", "benchmark", "threads", "resources", "message", "priority"]
with open("Snakefile", "r") as fin:
  for line in fin.readlines():
    line = line.strip()
    if line:
      if line.startswith("rule "):
        rule_name = line[5:-1].strip()
        rules[rule_name] = {}
      else:
        for keyword in keywords:
          if line.startswith(keyword):
            rules[rule_name][keyword] = line[len(keyword):].strip()[1:].strip()
            last_keyword = keyword
            flag = False
        if flag and last_keyword:
          rules[rule_name][last_keyword] = rules[rule_name][last_keyword] + line
        flag =True

def ptxt(text):
  return '"' + text.replace("'", "").replace('"', '') + '"'


input2rule = ""
rule2output = ""
rule2rule = set()
data_node = []
rule_node = set()
inputs, outputs = {}, {}
for rule_name, rule_content in rules.items():
  if "input" in rule_content:
    for input in rule_content["input"].split(","):
      input = input.strip()
      inputs[input] = rule_name
      data_node.append(input)
      input2rule = input2rule + "{input} -> {rule}\n".format(input=ptxt(input), rule=ptxt(rule_name))
  if "output" in rule_content:
    for output in rule_content["output"].split(","):
      output = output.strip()
      outputs[output] = rule_name
      data_node.append(output)
      rule2output = rule2output + "{rule} -> {output}\n".format(rule=ptxt(rule_name), output=ptxt(output))

for data, rule_name in inputs.items():
  rule_node.add(rule_name)
  if data in outputs.keys():
    rule1 = outputs[data]
    rule_node.add(rule1)
    rule2rule.add("{rule1} -> {rule2}".format(rule1=rule1, rule2=rule_name))

gv = "digraph G {" + """
rankdir=TB
fontname=Courier; fontsize=18; labelloc=t

node [shape=box style="filled, rounded", fillcolor = "#FFFFD1"]
{data_node}

node [shape=box3d style="filled, rounded", fillcolor = "#D6FDD0"]
{rule_node}

edge [color = black]
{data_edge}
""".format(data_node="\n".join([ptxt(x) for x in data_node]),
           rule_node="\n".join([ptxt(x) for x in rule_node]),
           data_edge=input2rule+rule2output,
           rule_edge="\n".join(rule2rule)) + "}"

print(gv)


