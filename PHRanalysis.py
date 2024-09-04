from flask import Flask, request, jsonify
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image
import requests
import io
import re
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

def extract_text_from_pdf(pdf):
    response = requests.get(pdf)
    if response.status_code == 200:
        pdf_data = io.BytesIO(response.content)
    else:
        raise Exception(f"Failed to download PDF. Status code: {response.status_code}")

    try:
        images = convert_from_bytes(pdf_data.read())
    except Exception as e:
        raise Exception(f"Failed to convert PDF to images. Error: {str(e)}")

    extracted_text = ""
    for page_num, img in enumerate(images):
        text = pytesseract.image_to_string(img)
        extracted_text += f"\n\n--- Page {page_num + 1} ---\n\n"
        extracted_text += text

    return extracted_text

def extract_basic_info(text):
    basic_info = {}
    patterns = {
        "Name": r"Name\s*\s*(.*)",
        "Lab No.": r"Lab No\.\s*:\s*(\d+)",
        "Age": r"Age\s*:\s*(\d+)\s*Years",
        "Ref By": r"Ref By\s*:\s*(.*)",
        "Gender": r"Gender\s*:\s*(\w+)",
        "Collected": r"Collected\s*:\s*(\d{1,2}/\d{1,2}/\d{4})\s*(\d{1,2}:\d{2}:\d{2}AM|PM)",
        "Reported": r"Reported\s*:\s*(\d{1,2}/\d{1,2}/\d{4})\s*(\d{1,2}:\d{2}:\d{2}AM|PM)",
        "A/c Status": r"A/c Status\s*:\s*(\w+)",
        "Report Status": r"Report Status\s*:\s*(\w+)",
        "Collected at": r"Collected at\s*:\s*(.*)",
        "Processed at": r"Processed at\s*:\s*(.*)"
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            basic_info[key] = match.group(1).strip()

    return basic_info

def extract_test_results(text):
    results = {}

    pattern = re.compile(r'(?P<test_name>[\w\s\(\)\-\;]+)\s+(?P<result>[\d\.]+)\s+(?P<units>[\w\/\%\.\-]+)\s+(?P<interval>[\d\.\<\>\-\s]+)')

    matches = pattern.finditer(text)

    for match in matches:
        test_name = match.group('test_name').strip()
        result = match.group('result').strip()
        units = match.group('units').strip()
        interval = match.group('interval').strip()

        results[test_name] = {
            "Result": result,
            "Units": units,
            "Bio. Ref. Interval": interval
        }

    return results

def analyze_report(test_results):
    summary = []
    # Your analysis code here...
    if 'Interval\nSwasthFit Super 4\nCOMPLETE BLOOD COUNT;CBC\nHemoglobin' in test_results:
        hb = float(test_results['Interval\nSwasthFit Super 4\nCOMPLETE BLOOD COUNT;CBC\nHemoglobin']['Result'])
        if hb < 13.0:
            summary.append(f"Hemoglobin is low ({hb} g/dL). Possible anemia.")
        elif hb > 17.0:
            summary.append(f"Hemoglobin is high ({hb} g/dL). Possible dehydration or other conditions.")
        else:
            summary.append(f"Hemoglobin is normal ({hb} g/dL).")

    # Check RBC Count
    if 'RBC Count\n(Electrical Impedence)' in test_results:
        rbc = float(test_results['RBC Count\n(Electrical Impedence)']['Result'])
        if rbc < 4.5:
            summary.append(f"RBC count is low ({rbc} mill/mm3). Could indicate anemia or other issues.")
        elif rbc > 5.5:
            summary.append(f"RBC count is high ({rbc} mill/mm3). Could indicate dehydration or polycythemia.")
        else:
            summary.append(f"RBC count is normal ({rbc} mill/mm3).")

    # Check Total Leukocyte Count (TLC)
    if 'Total Leukocyte Count (TLC)\n(Electrical Impedence)' in test_results:
        tlc = float(test_results['Total Leukocyte Count (TLC)\n(Electrical Impedence)']['Result'])
        if tlc < 4.0:
            summary.append(f"Total Leukocyte Count is low ({tlc} thou/mm3). This could indicate a weakened immune system.")
        elif tlc > 10.0:
            summary.append(f"Total Leukocyte Count is high ({tlc} thou/mm3). This could indicate an infection.")
        else:
            summary.append(f"Total Leukocyte Count is normal ({tlc} thou/mm3).")

    # Check Platelet Count
    if 'Platelet Count\n(Electrical impedence)' in test_results:
        platelets = float(test_results['Platelet Count\n(Electrical impedence)']['Result'])
        if platelets < 150.0:
            summary.append(f"Platelet count is low ({platelets} thou/mm3). Risk of bleeding or bruising.")
        elif platelets > 410.0:
            summary.append(f"Platelet count is high ({platelets} thou/mm3). Risk of clotting issues.")
        else:
            summary.append(f"Platelet count is normal ({platelets} thou/mm3).")
    # check Differential Leucocyte Count(DLC)
    if 'Differential Leucocyte Count (DLC)\n(VCS Technology)\nSegmented Neutrophils' in test_results:
        neutrophils = float(test_results['Differential Leucocyte Count (DLC)\n(VCS Technology)\nSegmented Neutrophils']['Result'])
        if neutrophils < 40.0:
            summary.append(f"Segmented Neutrophils are low ({neutrophils}%). Could indicate neutropenia or a viral infection.")
        elif neutrophils > 80.0:
            summary.append(f"Segmented Neutrophils are high ({neutrophils}%). Could indicate a bacterial infection.")
        else:
            summary.append(f"Segmented Neutrophils are normal ({neutrophils}%).")


    # Add more summaries based on other important test results as needed.


    # Packed Cell Volume (PCV)
    if '(Photometry)\nPacked Cell Volume (PCV)' in test_results:
        pcv = float(test_results['(Photometry)\nPacked Cell Volume (PCV)']['Result'])
        if pcv < 40.0:
            summary.append(f"Packed Cell Volume (PCV) is low ({pcv}%). Could indicate anemia.")
        elif pcv > 50.0:
            summary.append(f"Packed Cell Volume (PCV) is high ({pcv}%). Could indicate dehydration.")
        else:
            summary.append(f"Packed Cell Volume (PCV) is normal ({pcv}%).")

    # RBC Count
    if '(Calculated)\nRBC Count' in test_results:
        rbc = float(test_results['(Calculated)\nRBC Count']['Result'])
        if rbc < 4.5:
            summary.append(f"RBC count is low ({rbc} mill/mm3). Could indicate anemia or other issues.")
        elif rbc > 5.5:
            summary.append(f"RBC count is high ({rbc} mill/mm3). Could indicate dehydration or polycythemia.")
        else:
            summary.append(f"RBC count is normal ({rbc} mill/mm3).")

    # MCV
    if '(Electrical Impedence)\nMCV' in test_results:
        mcv = float(test_results['(Electrical Impedence)\nMCV']['Result'])
        if mcv < 83.0:
            summary.append(f"MCV is low ({mcv} fL). Could indicate microcytic anemia.")
        elif mcv > 101.0:
            summary.append(f"MCV is high ({mcv} fL). Could indicate macrocytic anemia.")
        else:
            summary.append(f"MCV is normal ({mcv} fL).")

    # MCH
    if '(Electrical Impedence)\nMCH' in test_results:
        mch = float(test_results['(Electrical Impedence)\nMCH']['Result'])
        if mch < 27.0:
            summary.append(f"MCH is low ({mch} pg). Could indicate hypochromic anemia.")
        elif mch > 32.0:
            summary.append(f"MCH is high ({mch} pg). Could indicate macrocytic anemia.")
        else:
            summary.append(f"MCH is normal ({mch} pg).")

    # MCHC
    if '(Calculated)\nMCHC' in test_results:
        mchc = float(test_results['(Calculated)\nMCHC']['Result'])
        if mchc < 31.5:
            summary.append(f"MCHC is low ({mchc} g/dL). Could indicate hypochromic anemia.")
        elif mchc > 34.5:
            summary.append(f"MCHC is high ({mchc} g/dL). Could indicate hereditary spherocytosis.")
        else:
            summary.append(f"MCHC is normal ({mchc} g/dL).")

    # Red Cell Distribution Width (RDW)
    if '(Calculated)\nRed Cell Distribution Width (RDW)' in test_results:
        rdw = float(test_results['(Calculated)\nRed Cell Distribution Width (RDW)']['Result'])
        if rdw > 14.0:
            summary.append(f"RDW is high ({rdw}%). Could indicate mixed anemia or iron deficiency.")
        else:
            summary.append(f"RDW is normal ({rdw}%).")

    # Total Leukocyte Count (TLC)
    if '(Electrical Impedence)\nTotal Leukocyte Count (TLC)' in test_results:
        tlc = float(test_results['(Electrical Impedence)\nTotal Leukocyte Count (TLC)']['Result'])
        if tlc < 4.0:
            summary.append(f"Total Leukocyte Count is low ({tlc} thou/mm3). This could indicate a weakened immune system.")
        elif tlc > 10.0:
            summary.append(f"Total Leukocyte Count is high ({tlc} thou/mm3). This could indicate an infection.")
        else:
            summary.append(f"Total Leukocyte Count is normal ({tlc} thou/mm3).")

    # Differential Leucocyte Count (DLC) - Segmented Neutrophils
    if '(Electrical Impedence)\nDifferential Leucocyte Count (DLC)\n(VCS Technology)\nSegmented Neutrophils' in test_results:
        neutrophils = float(test_results['(Electrical Impedence)\nDifferential Leucocyte Count (DLC)\n(VCS Technology)\nSegmented Neutrophils']['Result'])
        if neutrophils < 40.0:
            summary.append(f"Segmented Neutrophils are low ({neutrophils}%). Could indicate neutropenia or a viral infection.")
        elif neutrophils > 80.0:
            summary.append(f"Segmented Neutrophils are high ({neutrophils}%). Could indicate a bacterial infection.")
        else:
            summary.append(f"Segmented Neutrophils are normal ({neutrophils}%).")

    # Lymphocytes
    if 'Lymphocytes' in test_results:
        lymphocytes = float(test_results['Lymphocytes']['Result'])
        if lymphocytes < 1.0:
            summary.append(f"Lymphocytes are low ({lymphocytes} thou/mm3). Could indicate a compromised immune system.")
        elif lymphocytes > 3.0:
            summary.append(f"Lymphocytes are high ({lymphocytes} thou/mm3). Could indicate a viral infection or lymphoma.")
        else:
            summary.append(f"Lymphocytes are normal ({lymphocytes} thou/mm3).")

    # Platelet Count
    if 'Platelet Count' in test_results:
        platelets = float(test_results['Platelet Count']['Result'])
        if platelets < 150.0:
            summary.append(f"Platelet count is low ({platelets} thou/mm3). Risk of bleeding or bruising.")
        elif platelets > 410.0:
            summary.append(f"Platelet count is high ({platelets} thou/mm3). Risk of clotting issues.")
        else:
            summary.append(f"Platelet count is normal ({platelets} thou/mm3).")

    if 'Monocytes' in test_results:
        monocytes = float(test_results['Monocytes']['Result'])
        if monocytes < 0.20:
            summary.append(f"Monocytes count is low ({monocytes} thou/mm3). This could indicate a potential issue with the immune system.")
        elif monocytes > 1.00:
            summary.append(f"Monocytes count is high ({monocytes} thou/mm3). This could indicate chronic inflammation or infection.")
        else:
            summary.append(f"Monocytes count is normal ({monocytes} thou/mm3).")

    if 'Eosinophils' in test_results:
        eosinophils = float(test_results['Eosinophils']['Result'])
        if eosinophils < 0.02:
            summary.append(f"Eosinophils count is low ({eosinophils} thou/mm3). This could be a sign of an immune deficiency.")
        elif eosinophils > 0.50:
            summary.append(f"Eosinophils count is high ({eosinophils} thou/mm3). This may indicate an allergic reaction or parasitic infection.")
        else:
            summary.append(f"Eosinophils count is normal ({eosinophils} thou/mm3).")
    if 'Basophils' in test_results:
        basophils = float(test_results['Basophils']['Result'])
        if basophils < 0.02:
            summary.append(f"Basophils count is low ({basophils} thou/mm3). This may suggest a possible allergic reaction or immune deficiency.")
        elif basophils > 0.10:
            summary.append(f"Basophils count is high ({basophils} thou/mm3). This could indicate chronic inflammation or an allergic condition.")
        else:
            summary.append(f"Basophils count is normal ({basophils} thou/mm3).")

    return summary

def generate_precautions(test_results):
    precautions = []

    # Hemoglobin-related precautions
    if 'Interval\nSwasthFit Super 4\nCOMPLETE BLOOD COUNT;CBC\nHemoglobin' in test_results:
        hb = float(test_results['Interval\nSwasthFit Super 4\nCOMPLETE BLOOD COUNT;CBC\nHemoglobin']['Result'])
        if hb < 13.0:
            precautions.append("Consider iron-rich foods or supplements. Consult a doctor if fatigue persists.")
        elif hb > 17.0:
            precautions.append("Ensure adequate hydration. Consult a doctor to rule out underlying conditions.")

    # Packed Cell Volume (PCV)-related precautions
    if '(Photometry)\nPacked Cell Volume (PCV)' in test_results:
        pcv = float(test_results['(Photometry)\nPacked Cell Volume (PCV)']['Result'])
        if pcv < 40.0:
            precautions.append("Increase intake of iron-rich foods. Monitor for signs of anemia.")
        elif pcv > 50.0:
            precautions.append("Ensure proper hydration and consult a doctor if symptoms of dehydration occur.")

    # RBC-related precautions
    if '(Calculated)\nRBC Count' in test_results:
        rbc = float(test_results['(Calculated)\nRBC Count']['Result'])
        if rbc < 4.5:
            precautions.append("Increase intake of iron and vitamin B12. Consult a healthcare provider.")
        elif rbc > 5.5:
            precautions.append("Stay hydrated. Consult a doctor if experiencing headaches or dizziness.")

    # MCV-related precautions
    if '(Electrical Impedence)\nMCV' in test_results:
        mcv = float(test_results['(Electrical Impedence)\nMCV']['Result'])
        if mcv < 83.0:
            precautions.append("Consider iron and vitamin B6 supplements. Monitor for signs of microcytic anemia.")
        elif mcv > 101.0:
            precautions.append("Increase intake of folic acid and vitamin B12. Consult a doctor for possible macrocytic anemia.")

    # MCH-related precautions
    if '(Electrical Impedence)\nMCH' in test_results:
        mch = float(test_results['(Electrical Impedence)\nMCH']['Result'])
        if mch < 27.0:
            precautions.append("Consider iron-rich foods and supplements. Monitor for signs of anemia.")
        elif mch > 32.0:
            precautions.append("Consult a doctor for possible macrocytic anemia. Ensure adequate vitamin B12 intake.")

    # MCHC-related precautions
    if '(Calculated)\nMCHC' in test_results:
        mchc = float(test_results['(Calculated)\nMCHC']['Result'])
        if mchc < 31.5:
            precautions.append("Increase intake of iron-rich foods. Monitor for signs of anemia.")
        elif mchc > 34.5:
            precautions.append("Consult a doctor for possible hereditary conditions like spherocytosis.")

    # RDW-related precautions
    if '(Calculated)\nRed Cell Distribution Width (RDW)' in test_results:
        rdw = float(test_results['(Calculated)\nRed Cell Distribution Width (RDW)']['Result'])
        if rdw > 14.0:
            precautions.append("Consider iron or vitamin B12 supplements. Consult a doctor for mixed anemia possibilities.")

    # Total Leukocyte Count (TLC)-related precautions
    if '(Electrical Impedence)\nTotal Leukocyte Count (TLC)' in test_results:
        tlc = float(test_results['(Electrical Impedence)\nTotal Leukocyte Count (TLC)']['Result'])
        if tlc < 4.0:
            precautions.append("Avoid exposure to infections. Maintain a healthy diet to support the immune system.")
        elif tlc > 10.0:
            precautions.append("Consult a doctor to check for possible infections or inflammation.")

    # Differential Leucocyte Count (DLC) - Segmented Neutrophils-related precautions
    if '(Electrical Impedence)\nDifferential Leucocyte Count (DLC)\n(VCS Technology)\nSegmented Neutrophils' in test_results:
        neutrophils = float(test_results['(Electrical Impedence)\nDifferential Leucocyte Count (DLC)\n(VCS Technology)\nSegmented Neutrophils']['Result'])
        if neutrophils < 40.0:
            precautions.append("Monitor for signs of infection. Consult a doctor for possible neutropenia.")
        elif neutrophils > 80.0:
            precautions.append("Consult a doctor to check for bacterial infections or other inflammatory conditions.")

    # Lymphocytes-related precautions
    if 'Lymphocytes' in test_results:
        lymphocytes = float(test_results['Lymphocytes']['Result'])
        if lymphocytes < 1.0:
            precautions.append("Monitor for signs of a weakened immune system. Consult a doctor for further evaluation.")
        elif lymphocytes > 3.0:
            precautions.append("Consult a doctor for possible viral infections or lymphoproliferative disorders.")

    # Platelet Count-related precautions
    if 'Platelet Count' in test_results:
        platelets = float(test_results['Platelet Count']['Result'])
        if platelets < 150.0:
            precautions.append("Avoid activities that may cause bruising or injury. Consult a doctor if symptoms worsen.")
        elif platelets > 410.0:
            precautions.append("Stay hydrated and avoid smoking. Consult a doctor to monitor blood clotting risk.")
    if 'Basophils' in test_results:
        basophils = float(test_results['Basophils']['Result'])
        if basophils < 0.02:
            precautions.append("Consult a doctor if experiencing signs of an allergic reaction or immune deficiency.")
        elif basophils > 0.10:
            precautions.append("Consult a doctor to rule out possible allergic reactions or chronic inflammation.")
    if 'Eosinophils' in test_results:
        eosinophils = float(test_results['Eosinophils']['Result'])
        if eosinophils < 0.02:
            precautions.append("Consult a doctor if symptoms like shortness of breath or skin rashes occur.")
        elif eosinophils > 0.50:
            precautions.append("Consider allergy testing. Consult a doctor for possible parasitic infections or allergic conditions.")
    if 'Monocytes' in test_results:
        monocytes = float(test_results['Monocytes']['Result'])
        if monocytes < 0.20:
            precautions.append("Monitor for signs of infection. Consult a doctor if symptoms persist.")
        elif monocytes > 1.00:
            precautions.append("Consult a doctor to rule out chronic inflammation or infection.")


    # If no specific precautions are needed, add a general precaution
    if not precautions:
        precautions.append("No precautions needed. Your reports are normal. Just maintain a healthy lifestyle and continue regular check-ups.")

    return precautions


@app.route('/extract-info', methods=['POST'])
def extract_info():
    data = request.get_json()
    pdf_url = data.get('pdf_url')

    if not pdf_url:
        return jsonify({"error": "No PDF URL provided."}), 400

    try:
        text = extract_text_from_pdf(pdf_url)
        basic_info = extract_basic_info(text)
        test_results = extract_test_results(text)
        precautions = generate_precautions(text)
        summary = analyze_report(test_results)
        return jsonify({
            "basic_info": basic_info,
            "precautions" : precautions , 
            "summary": summary
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
