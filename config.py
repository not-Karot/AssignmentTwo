PATH_TO_INVESTING = "https://uk.investing.com/stock-screener/?sp=country::4|sector::a|industry::a|equityType::a<eq_market_cap;1"
PATH_TO_LINKEDIN = "https://uk.linkedin.com"
PATH_TO_YAHOO= "https://uk.finance.yahoo.com/screener/unsaved/feea093b-2a61-4c0b-a8f1-4d0c7bb9a59e?dependentField=sector&dependentValues=&offset=0&count=100"
path_to_list_of_companies_linkedin= "https://uk.linkedin.com/directory/companies?trk=homepage-basic_directory_companyDirectoryUrl"
create_company_table="""CREATE TABLE if not exists company  (
  id INTEGER primary auto_increment,
  name varchar(64) NOT NULL,
  website varchar(32),
  headquarter varchar(32),
  employees INTEGER,
  industry varchar(32),
  type varchar(32)
);"""
create_employee_table="""CREATE TABLE if not exists employee(
    id INTEGER primary auto_increment),
    name varchar(64)  not NULL,
    title varchar(128) not NULL,
    company_id integer
    );"""