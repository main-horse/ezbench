from evaluator import run_test
import sys
import importlib
import tests
import os
import llm
from evaluator import Env, Conversation

import multiprocessing as mp

def run_one_test(test, test_llm, eval_llm, vision_eval_llm):
    test.setup(Env(), Conversation(test_llm), test_llm, eval_llm, vision_eval_llm)

    for success, output in test():
        if success:
            return True
        else:
            pass
    return False
                    

def run_all_tests(test_llm):
    test_llm = llm.LLM(model)
    sr = {}
    for f in os.listdir("tests"):
        if not f.endswith(".py"): continue
        try:
            spec = importlib.util.spec_from_file_location(f[:-3], "tests/" + f)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        except:
            continue
        test_case = [x for x in dir(module) if x.startswith("Test") and x != "TestCase"]
        if len(test_case) == 0:
            #print("Failure", f)
            pass
        else:
            print(f)
            for t in test_case:
                tmp = sys.stdout
                #sys.stdout = open(os.devnull, 'w')

                test = getattr(module, t)

                ok = run_one_test(test, test_llm, llm.eval_llm, llm.vision_eval_llm)

                sys.stdout = tmp
                if ok:
                    print("Test Passes:", t)
                else:
                    print("Test Fails:", t, 'from', f)
                sr[f] = ok
    return sr


def generate_report(data, tags):
    # Recalculating all keys to ensure they are in the same order
    all_keys = sorted({key for inner_dict in data.values() for key in inner_dict.keys()})

    assert set(all_keys) == set(tags.keys())
    
    # Calculating mean correctness for each column (key in inner dictionaries)
    column_means = {key: sum(inner_dict.get(key, 0) for inner_dict in data.values()) / len(data) for key in all_keys}
    
    # Sorting columns by mean correctness
    sorted_columns = sorted(all_keys, key=lambda x: column_means[x], reverse=True)
    
    # Calculating mean correctness for each row (outer keys) and sorting them
    row_means = {outer_key: sum(value for value in inner_dict.values()) / len(inner_dict) for outer_key, inner_dict in data.items()}
    sorted_rows = sorted(data.keys(), key=lambda x: row_means[x], reverse=True)
    
    # Transposing the data: columns become rows and rows become columns.
    transposed_data = {}
    for column in sorted_columns:
        transposed_data[column] = {row: data[row][column] for row in sorted_rows if column in data[row]}
    
    # Sorting the transposed columns (originally rows) by their mean correctness
    sorted_transposed_columns = sorted(transposed_data.keys(), key=lambda x: column_means[x], reverse=True)
    
    # Sorting the transposed rows (originally columns) by their mean correctness
    sorted_transposed_rows = sorted(transposed_data[sorted_transposed_columns[0]].keys(), key=lambda x: row_means[x], reverse=True)
    
    # Creating the HTML content with transposed and sorted rows and columns
    html_content = "<html><head><style>td, th {border: 1px solid black; padding: 10px;}</style></head><body>"

    tag_values = set(sum([tags[key] for key in tags], []))
    
    for tag in tag_values:
        html_content += "<span><input type='checkbox' onclick='hiderows()' id='" + tag + "' name='" + tag + "' value='" + tag + "' checked='checked'><label for='" + tag + "'>" + tag + "</label> | </span>"

    html_content += """<script>
function hiderows() {
    var checkboxes = document.querySelectorAll('input[type="checkbox"]');
    var checked = Array.prototype.slice.call(checkboxes).filter(cb => cb.checked).map(cb => cb.value);
    var rows = document.querySelectorAll('tr');
    console.log(checked);
    // show a row if any of the tags applies
    Array.prototype.slice.call(rows).forEach((row,id) => {
    if (id == 0) return;
    // allow th special
    console.log(checked)
        if (checked.some(tag=>row.getAttribute('tag_'+tag))) {
            row.style.display = 'table-row';
        } else {
            row.style.display = 'none';
        }
    });
}
</script>
"""
    

    html_content += "<table>"
    # Adding the transposed sorted header row (originally columns, now rows)
    html_content += "<tr><th>Model</th><th>Tags</th>" + "".join([f"<th>{key}</th>" for key in sorted_transposed_rows]) + "</tr>"
    
    # Adding transposed sorted rows (originally keys from inner dictionaries, now columns)
    for column_key in sorted_transposed_columns:
        this_tags = tags[column_key]
        html_content += f"""<tr {' '.join('tag_%s="1"'%x for x in this_tags)}><th>{column_key}</th><td>{', '.join(this_tags)}</td>"""
        for row_key in sorted_transposed_rows:
            value = transposed_data[column_key].get(row_key)
            # Color coding the cell or leaving it blank if the value is None
            cell_html = f"<td style='background-color: {'#aaffaa' if value else '#ffaaaa'};'>{str(value)}</td>" if value is not None else "<td></td>"
            html_content += cell_html
        html_content += "</tr>"
    
    # Closing the table and HTML tags.
    html_content += "</table></body></html>"
    
    # Saving the HTML content to a new file
    html_file_path_transposed_sorted = "/tmp/color_coded_table.html"
    with open(html_file_path_transposed_sorted, "w") as file:
        file.write(html_content)

def get_tags():
    tags = {}
    for f in os.listdir("tests"):
        if not f.endswith(".py"): continue
        try:
            spec = importlib.util.spec_from_file_location(f[:-3], "tests/" + f)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        except:
            continue
        if 'TAGS' in dir(module):
            tags[f] = module.TAGS
    return tags
        

    
data = {}    
#for model in ["mistral-tiny", "mistral-small", "mistral-medium", "gpt-3.5-turbo", "gpt-4-1106-preview"]:#, "/Users/Nicholas/Downloads/llama-2-13b-chat.Q4_K_M.gguf"]:
#for model in ["/Users/Nicholas/Downloads/llama-2-13b-chat.Q4_K_M.gguf"]:
for model in ["gpt-3.5-turbo", "gemini-pro", "chat-bison", "mistral-medium", "mistral-small", "mistral-tiny", "gpt-4-1106-preview"]:
    data[model] = run_all_tests(model)

print(data)

tags = get_tags()

generate_report(data, tags)
