%% representa la identidad humana civil
PERSON {
    int id_person PK
    int CI
    varchar first_name
    varchar last_name
    DATE date_of_birth
}

%% representa el rol comercial frente al negocio
CUSTOMER {
    int id_customer PK
    int id_person FK
}

SUPPLIER {
    INT id_supplier
}
