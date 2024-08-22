import frappe

@frappe.whitelist(allow_guest=True)
def test():
    doc = frappe.get_doc("Chat History","Zack Kozac")
    pat = {
        "data":[]
    }

    current = {"role" : "assistant", "content" : f"Hi"}
    print(doc.history,'gghhi')
    pat["data"].append(current)

    # doc.history = json.dumps(pat)

    if doc.history:
        print('if cond',doc.history)
        json_data = json.loads(doc.history)
        json_data["data"].append(current)

        doc.history = json.dumps(json_data)
    else:
        print('dsjfhsd')
        doc.history = json.dumps(pat)
    # doc.insert(ignore_permissions=True)
    doc.save(ignore_permissions=True)

 
    # print(type(json_data['data']),json_data['data'])
    # return json_data['data']


#working
import frappe
import json

@frappe.whitelist(allow_guest=True)
def reset():

    try:
        # doc = frappe.get_doc(doctype, docname)
        doc = frappe.get_doc("Chat History","Zack Kozac")
        pat= {
        "data":[]
    }

        doc.history = json.dumps(pat)
        doc.save(ignore_permissions=True)
        return "Chat history reset successfully"
    except Exception as e:
        frappe.log_error(f"Error resetting chat history: {str(e)}")
        return "Error resetting chat history"
    