# Ingestion & Chunking Inspection: sample-tables.pdf
- **File Path**: `C:\GithubProjects\Rag_Full_Version\data\sample-tables.pdf`
- **Engine**: `docling_ast`
- **Quality Score ($Q_{score}$)**: **0.806 / 1.0** (Acceptable)
- **Structural Blocks**: 4 sections, 29 tables, 32 paragraphs
- **Total Chunks Generated**: 61 (29 table chunks, 32 prose chunks)

## 1. Detected Sections
  - [H1] Design and build accessible PDF tables Sample tables
  - [H1] trends, 1980 to 2010. Source: Barro-Lee March, 2010
  - [H1] Table 27: "table" with columns simulated by using tab stops
  - [H1] Table 28: year-end financial table (£, thousands) - headings problem revisited

## 2. Extracted & Normalized Tables
### Table 1: Table 1
- **Section Path**: `sample-tables.pdf > Design and build accessible PDF tables Sample tables`
- **Prose Link**: (No preceding prose)
- **Rows**: 2 | **Columns** (3): `['Column header (TH)', 'Column header (TH)', 'Column header (TH)']`

**Markdown Preview:**

**Table 1**

| Column header (TH) | Column header (TH) | Column header (TH) |
| --- | --- | --- |
| Data cell (TD) | Data cell (TD) | Row header (TH) |
| Data cell (TD) | Data cell (TD) | Row header(TH) |

### Table 2: Table 2: example of footnotes referenced from within a table
- **Section Path**: `sample-tables.pdf > Design and build accessible PDF tables Sample tables`
- **Prose Link**: (Linked to prose: `b_2`)
- **Rows**: 7 | **Columns** (4): `['Expenditure by function £ million', 'Expenditure by function £ million', '2009/10', '2010/11 1']`

**Markdown Preview:**

**Table 2: example of footnotes referenced from within a table**

| Expenditure by function £ million | Expenditure by function £ million | 2009/10 | 2010/11 1 |
| --- | --- | --- | --- |
| Policy functions | Financial | 22.5 | 30.57 |
|  | Information 2 | 10.2 | 14.8 |
|  | Contingency | 2.6 | 1.2 |
| Remunerated functions | Agency services 3 | 44.7 | 35.91 |
|  | Payments | 22.41 | 19.88 |
|  | Banking | 22.90 | 44.23 |
|  | Other | 12.69 | 10.32 |

### Table 3: Table 3: "film credits" style layout
- **Section Path**: `sample-tables.pdf > Design and build accessible PDF tables Sample tables`
- **Prose Link**: (Linked to prose: `b_7`)
- **Rows**: 5 | **Columns** (2): `['Main character', 'Daniel Radcliffe']`

**Markdown Preview:**

**Table 3: "film credits" style layout**

| Main character | Daniel Radcliffe |
| --- | --- |
| Rupert Grint | Sidekick 1 |
| Emma Watson | Sidekick 2 |
| Robbie Coltrane | Lovable ogre |
| Maggie Smith | Professor |
| Richard Harris | Headmaster |

### Table 4: Untitled Table
- **Section Path**: `sample-tables.pdf > Design and build accessible PDF tables Sample tables`
- **Prose Link**: (Linked to prose: `b_10`)
- **Rows**: 6 | **Columns** (2): `['Role', 'Actor']`

**Markdown Preview:**

| Role | Actor |
| --- | --- |
| Daniel Radcliffe | Main character |
| Rupert Grint | Sidekick 1 |
| Emma Watson | Sidekick 2 |
| Robbie Coltrane | Lovable ogre |
| Maggie Smith | Professor |
| Richard Harris | Headmaster |

### Table 5: Untitled Table
- **Section Path**: `sample-tables.pdf > Design and build accessible PDF tables Sample tables`
- **Prose Link**: (Linked to prose: `b_12`)
- **Rows**: 8 | **Columns** (4): `['', '2010', '2009', '2008']`

**Markdown Preview:**

|  | 2010 | 2009 | 2008 |
| --- | --- | --- | --- |
| Non-current assets |  |  |  |
| Property | 345 | 445 | 222 |
| Investment | 567 | 654 | 423 |
| Intangibles | 423 | 123 | 453 |
| Current assets |  |  |  |
| Trade and other receivables | 435 | 634 | 231 |
| Cash and cash equivalents | 524 | 123 | 482 |
| Other | 223 | 211 | 254 |

### Table 6: Untitled Table
- **Section Path**: `sample-tables.pdf > Design and build accessible PDF tables Sample tables`
- **Prose Link**: (Linked to prose: `b_14`)
- **Rows**: 8 | **Columns** (5): `['Rainfall (inches)', 'Americas', 'Asia', 'Europe', 'Africa']`

**Markdown Preview:**

| Rainfall (inches) | Americas | Asia | Europe | Africa |
| --- | --- | --- | --- | --- |
| 2010 | 2010 | 2010 | 2010 | 2010 |
| Average | 104 | 201 | 193 | 144 |
| 24 hour high | 15 | 26 | 27 | 18 |
| 12 hour high | 9 | 10 | 11 | 12 |
| 2009 | 2009 | 2009 | 2009 | 2009 |
| Average | 133 | 244 | 155 | 166 |
| 24 hour high | 27 | 28 | 29 | 20 |
| 12 hour high | 11 | 12 | 13 | 16 |

### Table 7: Untitled Table
- **Section Path**: `sample-tables.pdf > Design and build accessible PDF tables Sample tables`
- **Prose Link**: (Linked to prose: `b_14`)
- **Rows**: 3 | **Columns** (4): `['Non-current assets', '2010', '2009', '2008']`

**Markdown Preview:**

| Non-current assets | 2010 | 2009 | 2008 |
| --- | --- | --- | --- |
| Property | 345 | 445 | 222 |
| Investment | 567 | 654 | 423 |
| Intangibles | 423 | 123 | 453 |

### Table 8: Untitled Table
- **Section Path**: `sample-tables.pdf > Design and build accessible PDF tables Sample tables`
- **Prose Link**: (Linked to prose: `b_17`)
- **Rows**: 3 | **Columns** (4): `['Current assets', '2010', '2009', '2008']`

**Markdown Preview:**

| Current assets | 2010 | 2009 | 2008 |
| --- | --- | --- | --- |
| 435 |  | 634 | Trade and other receivables 231 |
| Cash and cash equivalents 524 |  | 123 | 482 |
| Other | 223 | 211 | 254 |

### Table 9: Untitled Table
- **Section Path**: `sample-tables.pdf > Design and build accessible PDF tables Sample tables`
- **Prose Link**: (Linked to prose: `b_19`)
- **Rows**: 3 | **Columns** (5): `['Rainfall (inches)', 'Americas', 'Asia', 'Europe', 'Africa']`

**Markdown Preview:**

| Rainfall (inches) | Americas | Asia | Europe | Africa |
| --- | --- | --- | --- | --- |
| Average | 133 244 |  | 155 | 166 |
| 24 hour high | 27 | 28 | 29 | 20 |
| 12 hour high | 11 | 12 | 13 | 16 |

### Table 10: Table 10: self-contained year-end statement (£, thousands) (multiple layout problems)
- **Section Path**: `sample-tables.pdf > Design and build accessible PDF tables Sample tables`
- **Prose Link**: (Linked to prose: `b_19`)
- **Rows**: 13 | **Columns** (5): `['', '2011', '2011', '2010 restated', '2010 restated']`

**Markdown Preview:**

**Table 10: self-contained year-end statement (£, thousands) (multiple layout problems)**

|  | 2011 | 2011 | 2010 restated | 2010 restated |
| --- | --- | --- | --- | --- |
| General income |  | 250,000 |  | 200,000 |
| Increase in value, WIP |  | 15,000 |  | 30,000 |
|  |  | 265,000 |  | 230,000 |
| Administrative costs |  |  |  |  |
| Staff costs | (200,000) |  | (150,000) |  |
| Early departures | (10,000) |  | (20,000) |  |
| Other | (25,000) |  | (10,000) |  |
| Depreciation | (10,000) |  
...

### Table 11: Table 11: self-contained year-end statement (£, thousands) (multiple problems resolved)
- **Section Path**: `sample-tables.pdf > Design and build accessible PDF tables Sample tables`
- **Prose Link**: (Linked to prose: `b_22`)
- **Rows**: 11 | **Columns** (4): `['', '', '2011', '2010 restated']`

**Markdown Preview:**

**Table 11: self-contained year-end statement (£, thousands) (multiple problems resolved)**

|  |  | 2011 | 2010 restated |
| --- | --- | --- | --- |
| Income | General income | 250,000 | 200,000 |
|  | Increase in value | 15,000 | 30,000 |
|  | Total income | 265,000 | 230,000 |
| Administrative costs | Staff costs | (200,000) | (150,000) |
|  | Early departures | (10,000) | (20,000) |
|  | Other operating costs | (25,000) | (10,000) |
|  | Depreciation | (10,000) | (10,000) |
| Programme costs
...

### Table 12: Table 12: merged data cells are not recommended
- **Section Path**: `sample-tables.pdf > Design and build accessible PDF tables Sample tables`
- **Prose Link**: (Linked to prose: `b_24`)
- **Rows**: 3 | **Columns** (5): `['Name', '2008.Yes', '2008.No', '2009.Yes', '2009.No']`

**Markdown Preview:**

**Table 12: merged data cells are not recommended**

| Name | 2008.Yes | 2008.No | 2009.Yes | 2009.No |
| --- | --- | --- | --- | --- |
| Bob | 2 | 5 | 6 | 7 |
| Sue | 3 | 8 | 4 | 7 |
| Sam | [data relating to both columns in a single cell spanning both] | [data relating to both columns in a single cell spanning both] | [data relating to single cell | both columns in both] |

### Table 13: Table 13: use of graphic symbols
- **Section Path**: `sample-tables.pdf > Design and build accessible PDF tables Sample tables`
- **Prose Link**: (Linked to prose: `b_26`)
- **Rows**: 3 | **Columns** (4): `['Question', 'Respondent A', 'Respondent B', 'Respondent C']`

**Markdown Preview:**

**Table 13: use of graphic symbols**

| Question | Respondent A | Respondent B | Respondent C |
| --- | --- | --- | --- |
| Are you a UK citizen?  |  |  |  |
| Are you currently employed? |  |  |  |
| Do you have a driving licence? |  |  |  |

### Table 14: Table 14: symbols replaced by real text
- **Section Path**: `sample-tables.pdf > Design and build accessible PDF tables Sample tables`
- **Prose Link**: (Linked to prose: `b_28`)
- **Rows**: 3 | **Columns** (4): `['Question', 'Respondent A', 'Respondent B', 'Respondent C']`

**Markdown Preview:**

**Table 14: symbols replaced by real text**

| Question | Respondent A | Respondent B | Respondent C |
| --- | --- | --- | --- |
| No | Yes | No | Are you a UK citizen? |
| Yes | No | Yes | Are you currently employed? |
| No |  | No Yes | Do you have a driving licence? |

### Table 15: Table 15: courses offered by Institution X. A = Bachelor of Science, B = Bachelor of Arts, C = Masters, D = Doctorate, E = Diploma
- **Section Path**: `sample-tables.pdf > Design and build accessible PDF tables Sample tables`
- **Prose Link**: (Linked to prose: `b_30`)
- **Rows**: 6 | **Columns** (5): `['', '2006', '2007', '2008', '2009']`

**Markdown Preview:**

**Table 15: courses offered by Institution X. A = Bachelor of Science, B = Bachelor of Arts, C = Masters, D = Doctorate, E = Diploma**

|  | 2006 | 2007 | 2008 | 2009 |
| --- | --- | --- | --- | --- |
| Economics | A, B | A, C | A, B | A, C |
| International relations | A, E | A, E | A, B | A, E |
| Philosophy | A | A | A | A, D |
| Politics | A, D | A, D | A, D | A |
| Mathematics | B, C | B | A, E | A, B |
| English | A, C | A, B | A,B | C |

### Table 16: Table 16: Masters courses offered by Institution X
- **Section Path**: `sample-tables.pdf > Design and build accessible PDF tables Sample tables`
- **Prose Link**: (Linked to prose: `b_32`)
- **Rows**: 6 | **Columns** (5): `['', '2006', '2007', '2008', '2009']`

**Markdown Preview:**

**Table 16: Masters courses offered by Institution X**

|  | 2006 | 2007 | 2008 | 2009 |
| --- | --- | --- | --- | --- |
| Economics | No | Yes | Yes | Yes |
| International relations | No | No | No | No |
| Philosophy | No | No | No | No |
| Politics | No | No | No | No |
| Mathematics | Yes | No | No | No |
| English | Yes | Yes | Yes | Yes |

### Table 17: Table 17: accounts, 2011 (£, thousands)
- **Section Path**: `sample-tables.pdf > Design and build accessible PDF tables Sample tables`
- **Prose Link**: (Linked to prose: `b_34`)
- **Rows**: 10 | **Columns** (2): `['Accounting item', '2011']`

**Markdown Preview:**

**Table 17: accounts, 2011 (£, thousands)**

| Accounting item | 2011 |
| --- | --- |
| Income General income | 200,000 |
| Increase in value, WIP | 30,000 |
| Income subtotal | 230,000 |
| Administrative costs Staff | 150,000 |
| Early departures | 20,000 |
| Other operating costs | 10,000 |
| Depreciation | 10,000 |
| Programme costs Impairment loss | 10,000 |
| Costs subtotal | 200,000 |
| Balance | 30,000 |

### Table 18: Table 18: accounts, 2011 (£, thousands)
- **Section Path**: `sample-tables.pdf > Design and build accessible PDF tables Sample tables`
- **Prose Link**: (Linked to prose: `b_36`)
- **Rows**: 10 | **Columns** (3): `['Accounting item', 'Accounting item', '2011']`

**Markdown Preview:**

**Table 18: accounts, 2011 (£, thousands)**

| Accounting item | Accounting item | 2011 |
| --- | --- | --- |
| Income | General income | 200,000 |
|  | Increase in value, WIP | 30,000 |
|  | Income subtotal | 230,000 |
| Administrative costs | Staff | (150,000) |
|  | Early departures | (20,000) |
|  | Other operating costs | (10,000) |
|  | Depreciation | (10,000) |
| Programme costs | Impairment loss | (10,000) |
|  | Costs subtotal | (200,000) |
| Balance | Balance | 30,000 |

### Table 19: Untitled Table
- **Section Path**: `sample-tables.pdf > trends, 1980 to 2010. Source: Barro-Lee March, 2010`
- **Prose Link**: (No preceding prose)
- **Rows**: 5 | **Columns** (5): `['Country', '1980', '1990', '2000', '2010']`

**Markdown Preview:**

| Country | 1980 | 1990 | 2000 | 2010 |
| --- | --- | --- | --- | --- |
| Afghanistan | 0.78 | 1.48 | 2.16 | 3.33 |
| Albania | 8.89 | 9.67 | 9.89 | 10.38 |
| Algeria | 4.74 | 3.33 | 5.50 | 7.24 |
| Andorra | 4.98 | 5.63 | 9.09 | 10.35 |
| Angola | - | - | 4.42 | 4.42 |

### Table 20: Table 20: footnotes referenced from within a table
- **Section Path**: `sample-tables.pdf > trends, 1980 to 2010. Source: Barro-Lee March, 2010`
- **Prose Link**: (No preceding prose)
- **Rows**: 7 | **Columns** (4): `['Expenditure by function £million', 'Expenditure by function £million', '2009/10', '2010/11 1']`

**Markdown Preview:**

**Table 20: footnotes referenced from within a table**

| Expenditure by function £million | Expenditure by function £million | 2009/10 | 2010/11 1 |
| --- | --- | --- | --- |
| Policy functions | Financial | 22.5 | 30.57 |
| Policy functions | Information 2 | 10.2 | 14.8 |
| Policy functions | Contingency | 2.6 | 1.2 |
| Remunerated functions | Agency services 3 | 44.7 | 35.91 |
| Remunerated functions | Payments | 22.41 | 19.88 |
| Remunerated functions | Banking | 22.90 | 44.23 |
| Remunerate
...

### Table 21: Table 21: footnotes replaced by additional table summary text
- **Section Path**: `sample-tables.pdf > trends, 1980 to 2010. Source: Barro-Lee March, 2010`
- **Prose Link**: (Linked to prose: `b_46`)
- **Rows**: 7 | **Columns** (4): `['Expenditure by function £million', 'Expenditure by function £million', '2009/10', '2010/11']`

**Markdown Preview:**

**Table 21: footnotes replaced by additional table summary text**

| Expenditure by function £million | Expenditure by function £million | 2009/10 | 2010/11 |
| --- | --- | --- | --- |
| Policy functions | Financial | 22.5 | 30.57 |
| Policy functions | Information | 10.2 | 14.8 |
| Policy functions | Contingency | 2.6 | 1.2 |
| Remunerated functions | Agency services | 44.7 | 35.91 |
| Remunerated functions | Payments | 22.41 | 19.88 |
| Remunerated functions | Banking | 22.90 | 44.23 |
| Remun
...

### Table 22: Table 22: referencing multiple endnotes from within a table
- **Section Path**: `sample-tables.pdf > trends, 1980 to 2010. Source: Barro-Lee March, 2010`
- **Prose Link**: (Linked to prose: `b_48`)
- **Rows**: 7 | **Columns** (4): `['Expenditure £m', 'Notes', '2010', '2011']`

**Markdown Preview:**

**Table 22: referencing multiple endnotes from within a table**

| Expenditure £m | Notes | 2010 | 2011 |
| --- | --- | --- | --- |
|  | on 1 | 10.2 | (Notes located page [n]) Information 14.8 |
| Contingency |  | 2.6 | 1.2 |
| Payments | 3 | 22.41 | 19.88 |
| Banking | 4 | 22.90 | services 44.23 |
| Interest |  | 0.23 | 0.10 |
| Dividends | 23 | 2.5 | 3.68 |
| Other | 9 | 12.69 | 10.32 |

### Table 23: Table 23: simulated table created using tabs and containing no structure
- **Section Path**: `sample-tables.pdf > trends, 1980 to 2010. Source: Barro-Lee March, 2010`
- **Prose Link**: (Linked to prose: `b_50`)
- **Rows**: 2 | **Columns** (5): `['Name', '2008.Entered', '2008.Completed', '2009.Entered', '2009.Completed']`

**Markdown Preview:**

**Table 23: simulated table created using tabs and containing no structure**

| Name | 2008.Entered | 2008.Completed | 2009.Entered | 2009.Completed |
| --- | --- | --- | --- | --- |
| Bob | 22 | 21 | 20 | 19 |
| Sue | 44 | 12 | 12 | 10 |

### Table 24: Table 24: year-end financial statement (£, thousands)
- **Section Path**: `sample-tables.pdf > trends, 1980 to 2010. Source: Barro-Lee March, 2010`
- **Prose Link**: (Linked to prose: `b_52`)
- **Rows**: 12 | **Columns** (4): `['', '2010', '2009', '2008']`

**Markdown Preview:**

**Table 24: year-end financial statement (£, thousands)**

|  | 2010 | 2009 | 2008 |
| --- | --- | --- | --- |
| Non-current assets |  |  |  |
| Buildings | 345 | 445 | 222 |
| Investment | 567 | 654 | 423 |
| Intangibles | 423 | 123 | 453 |
| Current assets |  |  |  |
| Trade | 435 | 634 | 231 |
| Cash | 524 | 123 | 482 |
| Other | 223 | 211 | 254 |
| Current liabilities |  |  |  |
| Trade liabilities | 154 | 125 | 421 |
| Financial debt | 231 | 474 | 572 |
| Provisions | 111 | 312 | 347 |

### Table 25: Table 25: setting column and row scope via the tags panel
- **Section Path**: `sample-tables.pdf > trends, 1980 to 2010. Source: Barro-Lee March, 2010`
- **Prose Link**: (Linked to prose: `b_54`)
- **Rows**: 3 | **Columns** (5): `['Name', '2008.Entered', '2008.Won', '2009.Entered', '2009.Won']`

**Markdown Preview:**

**Table 25: setting column and row scope via the tags panel**

| Name | 2008.Entered | 2008.Won | 2009.Entered | 2009.Won |
| --- | --- | --- | --- | --- |
| Bob | 22 | 21 | 20 | 19 |
| Sue | 44 | 12 | 12 | 10 |
| Sam | 16 | 4 | 45 | 30 |

### Table 26: Table 26: courses offered by Institution X. A = Bachelor of Science, B = Bachelor of Arts, C = Masters, D = Doctorate, E = Diploma
- **Section Path**: `sample-tables.pdf > trends, 1980 to 2010. Source: Barro-Lee March, 2010`
- **Prose Link**: (Linked to prose: `b_56`)
- **Rows**: 6 | **Columns** (5): `['', '2006', '2007', '2008', '2009']`

**Markdown Preview:**

**Table 26: courses offered by Institution X. A = Bachelor of Science, B = Bachelor of Arts, C = Masters, D = Doctorate, E = Diploma**

|  | 2006 | 2007 | 2008 | 2009 |
| --- | --- | --- | --- | --- |
| Economics | A, B | A, C | A, C | A, C |
| International relations | A, E | A, E | A, B | A, B |
| Philosophy | A | A | A | A |
| Politics | A, D | A, D | A, B | A |
| Mathematics | B, C | B | A, B | A, B |
| English | A, C | A, B | A,B | A, C |

### Table 27: Untitled Table
- **Section Path**: `sample-tables.pdf > Table 27: "table" with columns simulated by using tab stops`
- **Prose Link**: (No preceding prose)
- **Rows**: 3 | **Columns** (3): `['Name', 'Apples', 'Pears']`

**Markdown Preview:**

| Name | Apples | Pears |
| --- | --- | --- |
| 20 | 25 | Bob Scott |
| 24 | 15 | Susan. P. Arnold-Jones, BA, FRSA, MD |
| 14 | 10 | Sam Holder-Dickinson |

### Table 28: Untitled Table
- **Section Path**: `sample-tables.pdf > Table 28: year-end financial table (£, thousands) - headings problem revisited`
- **Prose Link**: (No preceding prose)
- **Rows**: 12 | **Columns** (4): `['', '2010', '2009', '2008']`

**Markdown Preview:**

|  | 2010 | 2009 | 2008 |
| --- | --- | --- | --- |
| Non-current assets |  |  |  |
| Buildings | 345 | 445 | 222 |
| Investment | 567 | 654 | 423 |
| Intangibles | 423 | 123 | 453 |
| Current assets |  |  |  |
| Trade | 435 | 634 | 231 |
| Cash | 524 | 123 | 482 |
| Other | 223 | 211 | 254 |
| Current liabilities |  |  |  |
| Trade liabilities | 154 | 125 | 421 |
| Financial debt | 231 | 474 | 572 |
| Provisions | 111 | 312 | 347 |

### Table 29: Untitled Table
- **Section Path**: `sample-tables.pdf > Table 28: year-end financial table (£, thousands) - headings problem revisited`
- **Prose Link**: (Linked to prose: `b_63`)
- **Rows**: 12 | **Columns** (5): `['', 'South America', 'Asia', 'Africa', 'Australia']`

**Markdown Preview:**

|  | South America | Asia | Africa | Australia |
| --- | --- | --- | --- | --- |
| 2010 | 2010 | 2010 | 2010 | 2010 |
| Highest average | 523.6 | 467.4 | 405.0 | 340.5 |
| Highest in 24 hours | 73.1 | 54.1 | 27.2 | 66.3 |
| Highest in 12 hours | 42.4 | 30.1 | 15.9 | 40.3 |
| 2009 | 2009 | 2009 | 2009 | 2009 |
| Highest average | 487.7 | 453.6 | 398.7 | 356 |
| Highest in 24 hours | 67.2 | 53.2 | 44.3 | 53.8 |
| Highest in 12 hours | 34.7 | 34.1 | 29.8 | 31.0 |
| 2008 | 2008 | 2008 | 2008 | 2008 
...
