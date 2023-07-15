import yaml
import json
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output_file', type=str, default='ai.example', help='output file')
    parser.add_argument('--input_file', type=str, default='ai.yml', help='input file')
    args = parser.parse_args()

    output_f = open(args.output_file,"w")
    with open(args.input_file,"r") as f:
        python_dict=yaml.load(f.read(),Loader=yaml.Loader)

        categories = python_dict['categories'][0]
        conversations = python_dict['conversations']
        output_json = []
        for conversation in conversations:
            output_json.append({"query":conversation[0], "intention":categories, "reply":conversation[1]})
        output = json.dumps(output_json, ensure_ascii=False)
        output_f.write(output)

    output_f.close()