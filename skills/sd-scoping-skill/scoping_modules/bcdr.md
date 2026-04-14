## BC/DR 

### Focus Areas 
- Business Continiuty 
- Disaster Recovery 
- replication 
- Client re direct 

### Key Objects
**Always confirm inventory for below Objects:**
- Number of Databases
- Size of Databasse
- Number of Users
- Number of Roles
- Number of Warehouse
- Number of Non replicated Objects like external tables , streamlit apps. Check for 
- Number of pipelines 
- Downstream apps 
- Downstream data shares/listing or Native apps 
- Source systems 

### Risk Areas
- Non replicated Objects
- External Integrations 
- Cutover timelines 

###  complexity driver 

#### Number of Acccounts 
- Understand how many accounts in scope 

#### Number of Objects (Databases , Warehouse , Users , Roles )
#### Non replicated Objects
- Check Snowflake documentation to understand non replicated objects and confirm with user 
#### Shares/Listings 
#### Native Apps/ Cleanrooms 

###  Typical Phases

> ** Only use Phases defined in below table. Don't add any other unless asked by User**

- Use Phases from 
     - snowflake connection : snowhouse 
     - table : TEMP.APP_BC_DR.BCDR_ACTIVITIES
     - Columns : TASK_ID, PHASE, MILESTONE, KEY_ACTIVITY, OWNERSHIP, TASK_DESCRIPTION, DELIVERABLES, MANDATORY, DEFAULT_COMPLEXITY, TIMELINE

###  Baseline  Effort 
> ** Only use Hours defined in below table. Don't add any other unless asked by User**

- Use baseline hours from 
     - snowflake connection : snowhouse 
     - table : TEMP.APP_BC_DR.BCDR_ACTIVITIES
     - Columns : TASK_ID, PHASE, MILESTONE, KEY_ACTIVITY, OWNERSHIP, TASK_DESCRIPTION, DELIVERABLES, MANDATORY, DEFAULT_COMPLEXITY, TIMELINE
