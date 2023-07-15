import json
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output_file', type=str, default='aws_faq.example', help='output file')
    parser.add_argument('--input_file', type=str, default='aws_qa_cn_instruction_alpaca.json', help='input file')
    args = parser.parse_args()

    output_f = open(args.output_file,"w")
    with open(args.input_file,"r") as f:
        instruction_arr=json.loads(f.read())

        output_json = []
        for instruction in instruction_arr:
            if instruction['instruction'].find("费用") == -1 and instruction['instruction'].find("价格") == -1 and instruction['instruction'].find("收费") == -1:
                output_json.append({"query":instruction['instruction'], "intention":'知识问答', "reply":instruction['output']})

        output = json.dumps(output_json, ensure_ascii=False)
        output_f.write(output)

    output_f.close()