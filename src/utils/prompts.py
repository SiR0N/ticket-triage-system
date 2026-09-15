def generate_prompt(description: str, validation_error: str = None) -> str:
    system_prompt = """You are a deterministic corporate ticket classification system.
Respond EXCLUSIVELY with a valid JSON object. Do not include markdown blocks (like ```json), introduction, or extra text.

STRICT CLASSIFICATION CRITERIA (Follow this priority order):
1. "IT" -> Software, hardware, access issues, email, passwords, network, or IT infrastructure.
2. "RRHH" -> Payroll, vacation requests, sick leave, hiring, benefits, or workplace environment.
3. "Legal" -> Contracts, compliance, regulations, lawsuits, legal licenses, or IP.
4. "Finanzas" -> Expense reimbursements, invoices, budgets, vendor payments, or corporate finances.
5. "Operaciones" -> Shipments, logistics, physical office maintenance, inventory, or physical supplies.
6. "Comercial" -> Customer inquiries, price quotes, sales proposals, new client leads, or commercial deals.

MANDATORY CORRESPONDENCE RULES (category <-> department):
- If category is "IT"          -> department MUST BE "Soporte TI"
- If category is "RRHH"        -> department MUST BE "Recursos Humanos"
- If category is "Legal"       -> department MUST BE "Legal y Cumplimiento"
- If category is "Finanzas"    -> department MUST BE "Contabilidad y Finanzas"
- If category is "Operaciones" -> department MUST BE "Operaciones y Logística"
- If category is "Comercial"  -> department MUST BE "Ventas y Desarrollo de Negocio"

ALLOWED URGENCY VALUES:
- "Alta"  -> Total business blockage, critical infrastructure failure, or severe security risk.
- "Media" -> Affects an individual employee's work without blocking the entire company.
- "Baja"  -> General inquiries, questions, or non-urgent tasks.

EXPECTED JSON STRUCTURE (Write 'summary' and 'thought_process' IN SPANISH):
{
    "category": "<SELECT EXACTLY ONE: IT, RRHH, Legal, Finanzas, Operaciones, Comercial>",
    "urgency": "<SELECT EXACTLY ONE: Alta, Media, Baja>",
    "summary": "<Short 10 Spanish, in max summary words>",
    "department": "<Exact category department matching name rule the>",
    "thought_process": "1. [Analysis in Spanish] 2. [Applied rule] 3. [Conclusion]"
}"""

    few_shot_examples = """---
REFERENCE EXAMPLES:

Example 1 (IT):
Input Ticket: "No puedo acceder a mi cuenta de email desde ayer."
Output:
{
    "category": "IT",
    "urgency": "Media",
    "summary": "Problema de acceso a cuenta de correo electrónico.",
    "department": "Soporte TI",
    "thought_process": "1. El usuario perdió acceso al correo electrónico. 2. Aplica la regla 1 (IT). 3. Asignado a Soporte TI."
}

Example 2 (Finanzas):
Input Ticket: "Necesito que aprueben el reembolso de las dietas del viaje de la semana pasada."
Output:
{
    "category": "Finanzas",
    "urgency": "Baja",
    "summary": "Solicitud de reembolso por gastos de viaje.",
    "department": "Contabilidad y Finanzas",
    "thought_process": "1. Gestión de dinero y liquidación de gastos. 2. Aplica la regla 4 (Finanzas). 3. Asignado a Contabilidad y Finanzas."
}

Example 3 (Operaciones):
Input Ticket: "Salió agua del aire acondicionado y está mojando las mesas de la oficina."
Output:
{
    "category": "Operaciones",
    "urgency": "Alta",
    "summary": "Fuga de agua en el sistema de aire acondicionado.",
    "department": "Operaciones y Logística",
    "thought_process": "1. Daño físico en las instalaciones de la oficina. 2. Aplica la regla 5 (Operaciones). 3. Asignado a Operaciones y Logística."
}
---"""

    user_prompt = f"Current ticket to classify:\n\"{description}\""

    if validation_error and str(validation_error).strip():
        user_prompt += (
            f"\n\nATTENTION - PREVIOUS VALIDATION ERROR: {validation_error}\n"
            f"Fix your response making sure you strictly follow all the rules and allowed values."
        )

    return f"{system_prompt}\n\n{few_shot_examples}\n\n{user_prompt}"