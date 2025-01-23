import xml.etree.ElementTree as ET

def parser(xml_path):
    # XML 파싱
    root = ET.parse(xml_path)
    root = ET.tostring(root)

    # Markdown 변환
    markdown_output = []

    # Report Title
    markdown_output.append(f"# {root.attrib['name']} Report\n")

    # Class Information
    for cls in root.findall('.//class'):
        class_name = cls.attrib['name']
        source_file = cls.attrib['sourcefilename']
        markdown_output.append(f"## Class: {class_name} (Source: {source_file})\n")
        
        # Method Information
        markdown_output.append("| Method Name | Instructions Covered | Lines Covered | Complexity Covered | Branches Covered | Methods Covered |\n")
        markdown_output.append("|-------------|----------------------|---------------|--------------------|------------------|-----------------|\n")
        
        for method in cls.findall('method'):
            method_name = method.attrib['name']
            instruction_covered = method.find("counter[@type='INSTRUCTION']").attrib['covered']
            line_covered = method.find("counter[@type='LINE']").attrib['covered']
            complexity_covered = method.find("counter[@type='COMPLEXITY']").attrib['covered']
            branch_covered = method.find("counter[@type='BRANCH']").attrib['covered'] if method.find("counter[@type='BRANCH']") is not None else '0'
            method_covered = method.find("counter[@type='METHOD']").attrib['covered']
            
            markdown_output.append(f"| {method_name} | {instruction_covered} | {line_covered} | {complexity_covered} | {branch_covered} | {method_covered} |\n")
        
        # Class Summary
        total_instruction_covered = cls.find("counter[@type='INSTRUCTION']").attrib['covered']
        total_branch_covered = cls.find("counter[@type='BRANCH']").attrib['covered']
        total_line_covered = cls.find("counter[@type='LINE']").attrib['covered']
        total_complexity_covered = cls.find("counter[@type='COMPLEXITY']").attrib['covered']
        total_method_covered = cls.find("counter[@type='METHOD']").attrib['covered']
        
        markdown_output.append(f"### Summary\n")
        markdown_output.append(f"- Total Instructions Covered: {total_instruction_covered}\n")
        markdown_output.append(f"- Total Branches Covered: {total_branch_covered}\n")
        markdown_output.append(f"- Total Lines Covered: {total_line_covered}\n")
        markdown_output.append(f"- Total Complexity Covered: {total_complexity_covered}\n")
        markdown_output.append(f"- Total Methods Covered: {total_method_covered}\n")

    # Markdown 출력
    markdown_result = ''.join(markdown_output)
    return markdown_result