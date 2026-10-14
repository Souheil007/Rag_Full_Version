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
- **Table ID**: `b_1`
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
- **Table ID**: `b_3`
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
- **Table ID**: `b_8`
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
- **Table ID**: `b_11`
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
- **Table ID**: `b_13`
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
- **Table ID**: `b_15`
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
- **Table ID**: `b_16`
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
- **Table ID**: `b_18`
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
- **Table ID**: `b_20`
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
- **Table ID**: `b_21`
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
- **Table ID**: `b_23`
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
- **Table ID**: `b_25`
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
- **Table ID**: `b_27`
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
- **Table ID**: `b_29`
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
- **Table ID**: `b_31`
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
- **Table ID**: `b_33`
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
- **Table ID**: `b_35`
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
- **Table ID**: `b_37`
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
- **Table ID**: `b_41`
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
- **Table ID**: `b_42`
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
- **Table ID**: `b_47`
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
- **Table ID**: `b_49`
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
- **Table ID**: `b_51`
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
- **Table ID**: `b_53`
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
- **Table ID**: `b_55`
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
- **Table ID**: `b_57`
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
- **Table ID**: `b_60`
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
- **Table ID**: `b_62`
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
- **Table ID**: `b_64`
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


## 3. All Generated Chunks & Relational Provenance
| # | Chunk ID | Block Type | Section Path | Relational Links / Metadata |
| :--- | :--- | :--- | :--- | :--- |
| 1 | `b_1_atomic` | `table` | sample-tables.pdf > Design and build accessible PDF tables Sample tables | Table: `b_1`, Atomic (Full) |
| 2 | `b_2` | `paragraph` | sample-tables.pdf > Design and build accessible PDF tables Sample tables | Parent: `b_0`, Page: 1 |
| 3 | `b_3_atomic` | `table` | sample-tables.pdf > Design and build accessible PDF tables Sample tables | Table: `b_3`, Intro Prose: `b_2`, Atomic (Full) |
| 4 | `b_4` | `paragraph` | sample-tables.pdf > Design and build accessible PDF tables Sample tables | Parent: `b_0`, Page: 1 |
| 5 | `b_5` | `paragraph` | sample-tables.pdf > Design and build accessible PDF tables Sample tables | Parent: `b_0`, Page: 1 |
| 6 | `b_6` | `paragraph` | sample-tables.pdf > Design and build accessible PDF tables Sample tables | Parent: `b_0`, Page: 1 |
| 7 | `b_7` | `paragraph` | sample-tables.pdf > Design and build accessible PDF tables Sample tables | Parent: `b_0`, Page: 1 |
| 8 | `b_8_atomic` | `table` | sample-tables.pdf > Design and build accessible PDF tables Sample tables | Table: `b_8`, Intro Prose: `b_7`, Atomic (Full) |
| 9 | `b_9` | `paragraph` | sample-tables.pdf > Design and build accessible PDF tables Sample tables | Parent: `b_0`, Page: 1 |
| 10 | `b_10` | `paragraph` | sample-tables.pdf > Design and build accessible PDF tables Sample tables | Parent: `b_0`, Page: 1 |
| 11 | `b_11_atomic` | `table` | sample-tables.pdf > Design and build accessible PDF tables Sample tables | Table: `b_11`, Intro Prose: `b_10`, Atomic (Full) |
| 12 | `b_12` | `paragraph` | sample-tables.pdf > Design and build accessible PDF tables Sample tables | Parent: `b_0`, Page: 1 |
| 13 | `b_13_atomic` | `table` | sample-tables.pdf > Design and build accessible PDF tables Sample tables | Table: `b_13`, Intro Prose: `b_12`, Atomic (Full) |
| 14 | `b_14` | `paragraph` | sample-tables.pdf > Design and build accessible PDF tables Sample tables | Parent: `b_0`, Page: 1 |
| 15 | `b_15_atomic` | `table` | sample-tables.pdf > Design and build accessible PDF tables Sample tables | Table: `b_15`, Intro Prose: `b_14`, Atomic (Full) |
| 16 | `b_16_atomic` | `table` | sample-tables.pdf > Design and build accessible PDF tables Sample tables | Table: `b_16`, Intro Prose: `b_14`, Atomic (Full) |
| 17 | `b_17` | `paragraph` | sample-tables.pdf > Design and build accessible PDF tables Sample tables | Parent: `b_0`, Page: 1 |
| 18 | `b_18_atomic` | `table` | sample-tables.pdf > Design and build accessible PDF tables Sample tables | Table: `b_18`, Intro Prose: `b_17`, Atomic (Full) |
| 19 | `b_19` | `paragraph` | sample-tables.pdf > Design and build accessible PDF tables Sample tables | Parent: `b_0`, Page: 1 |
| 20 | `b_20_atomic` | `table` | sample-tables.pdf > Design and build accessible PDF tables Sample tables | Table: `b_20`, Intro Prose: `b_19`, Atomic (Full) |
| 21 | `b_21_atomic` | `table` | sample-tables.pdf > Design and build accessible PDF tables Sample tables | Table: `b_21`, Intro Prose: `b_19`, Atomic (Full) |
| 22 | `b_22` | `paragraph` | sample-tables.pdf > Design and build accessible PDF tables Sample tables | Parent: `b_0`, Page: 1 |
| 23 | `b_23_atomic` | `table` | sample-tables.pdf > Design and build accessible PDF tables Sample tables | Table: `b_23`, Intro Prose: `b_22`, Atomic (Full) |
| 24 | `b_24` | `paragraph` | sample-tables.pdf > Design and build accessible PDF tables Sample tables | Parent: `b_0`, Page: 1 |
| 25 | `b_25_atomic` | `table` | sample-tables.pdf > Design and build accessible PDF tables Sample tables | Table: `b_25`, Intro Prose: `b_24`, Atomic (Full) |
| 26 | `b_26` | `paragraph` | sample-tables.pdf > Design and build accessible PDF tables Sample tables | Parent: `b_0`, Page: 1 |
| 27 | `b_27_atomic` | `table` | sample-tables.pdf > Design and build accessible PDF tables Sample tables | Table: `b_27`, Intro Prose: `b_26`, Atomic (Full) |
| 28 | `b_28` | `paragraph` | sample-tables.pdf > Design and build accessible PDF tables Sample tables | Parent: `b_0`, Page: 1 |
| 29 | `b_29_atomic` | `table` | sample-tables.pdf > Design and build accessible PDF tables Sample tables | Table: `b_29`, Intro Prose: `b_28`, Atomic (Full) |
| 30 | `b_30` | `paragraph` | sample-tables.pdf > Design and build accessible PDF tables Sample tables | Parent: `b_0`, Page: 1 |
| 31 | `b_31_atomic` | `table` | sample-tables.pdf > Design and build accessible PDF tables Sample tables | Table: `b_31`, Intro Prose: `b_30`, Atomic (Full) |
| 32 | `b_32` | `paragraph` | sample-tables.pdf > Design and build accessible PDF tables Sample tables | Parent: `b_0`, Page: 1 |
| 33 | `b_33_atomic` | `table` | sample-tables.pdf > Design and build accessible PDF tables Sample tables | Table: `b_33`, Intro Prose: `b_32`, Atomic (Full) |
| 34 | `b_34` | `paragraph` | sample-tables.pdf > Design and build accessible PDF tables Sample tables | Parent: `b_0`, Page: 1 |
| 35 | `b_35_atomic` | `table` | sample-tables.pdf > Design and build accessible PDF tables Sample tables | Table: `b_35`, Intro Prose: `b_34`, Atomic (Full) |
| 36 | `b_36` | `paragraph` | sample-tables.pdf > Design and build accessible PDF tables Sample tables | Parent: `b_0`, Page: 1 |
| 37 | `b_37_atomic` | `table` | sample-tables.pdf > Design and build accessible PDF tables Sample tables | Table: `b_37`, Intro Prose: `b_36`, Atomic (Full) |
| 38 | `b_38` | `paragraph` | sample-tables.pdf > Design and build accessible PDF tables Sample tables | Parent: `b_0`, Page: 1 |
| 39 | `b_39` | `paragraph` | sample-tables.pdf > Design and build accessible PDF tables Sample tables | Parent: `b_0`, Page: 1 |
| 40 | `b_41_atomic` | `table` | sample-tables.pdf > trends, 1980 to 2010. Source: Barro-Lee March, 2010 | Table: `b_41`, Atomic (Full) |
| 41 | `b_42_atomic` | `table` | sample-tables.pdf > trends, 1980 to 2010. Source: Barro-Lee March, 2010 | Table: `b_42`, Atomic (Full) |
| 42 | `b_43` | `paragraph` | sample-tables.pdf > trends, 1980 to 2010. Source: Barro-Lee March, 2010 | Parent: `b_40`, Page: 1 |
| 43 | `b_44` | `paragraph` | sample-tables.pdf > trends, 1980 to 2010. Source: Barro-Lee March, 2010 | Parent: `b_40`, Page: 1 |
| 44 | `b_45` | `paragraph` | sample-tables.pdf > trends, 1980 to 2010. Source: Barro-Lee March, 2010 | Parent: `b_40`, Page: 1 |
| 45 | `b_46` | `paragraph` | sample-tables.pdf > trends, 1980 to 2010. Source: Barro-Lee March, 2010 | Parent: `b_40`, Page: 1 |
| 46 | `b_47_atomic` | `table` | sample-tables.pdf > trends, 1980 to 2010. Source: Barro-Lee March, 2010 | Table: `b_47`, Intro Prose: `b_46`, Atomic (Full) |
| 47 | `b_48` | `paragraph` | sample-tables.pdf > trends, 1980 to 2010. Source: Barro-Lee March, 2010 | Parent: `b_40`, Page: 1 |
| 48 | `b_49_atomic` | `table` | sample-tables.pdf > trends, 1980 to 2010. Source: Barro-Lee March, 2010 | Table: `b_49`, Intro Prose: `b_48`, Atomic (Full) |
| 49 | `b_50` | `paragraph` | sample-tables.pdf > trends, 1980 to 2010. Source: Barro-Lee March, 2010 | Parent: `b_40`, Page: 1 |
| 50 | `b_51_atomic` | `table` | sample-tables.pdf > trends, 1980 to 2010. Source: Barro-Lee March, 2010 | Table: `b_51`, Intro Prose: `b_50`, Atomic (Full) |
| 51 | `b_52` | `paragraph` | sample-tables.pdf > trends, 1980 to 2010. Source: Barro-Lee March, 2010 | Parent: `b_40`, Page: 1 |
| 52 | `b_53_atomic` | `table` | sample-tables.pdf > trends, 1980 to 2010. Source: Barro-Lee March, 2010 | Table: `b_53`, Intro Prose: `b_52`, Atomic (Full) |
| 53 | `b_54` | `paragraph` | sample-tables.pdf > trends, 1980 to 2010. Source: Barro-Lee March, 2010 | Parent: `b_40`, Page: 1 |
| 54 | `b_55_atomic` | `table` | sample-tables.pdf > trends, 1980 to 2010. Source: Barro-Lee March, 2010 | Table: `b_55`, Intro Prose: `b_54`, Atomic (Full) |
| 55 | `b_56` | `paragraph` | sample-tables.pdf > trends, 1980 to 2010. Source: Barro-Lee March, 2010 | Parent: `b_40`, Page: 1 |
| 56 | `b_57_atomic` | `table` | sample-tables.pdf > trends, 1980 to 2010. Source: Barro-Lee March, 2010 | Table: `b_57`, Intro Prose: `b_56`, Atomic (Full) |
| 57 | `b_58` | `paragraph` | sample-tables.pdf > trends, 1980 to 2010. Source: Barro-Lee March, 2010 | Parent: `b_40`, Page: 1 |
| 58 | `b_60_atomic` | `table` | sample-tables.pdf > Table 27: "table" with columns simulated by using tab stops | Table: `b_60`, Atomic (Full) |
| 59 | `b_62_atomic` | `table` | sample-tables.pdf > Table 28: year-end financial table (£, thousands) - headings problem revisited | Table: `b_62`, Atomic (Full) |
| 60 | `b_63` | `paragraph` | sample-tables.pdf > Table 28: year-end financial table (£, thousands) - headings problem revisited | Parent: `b_61`, Page: 1 |
| 61 | `b_64_atomic` | `table` | sample-tables.pdf > Table 28: year-end financial table (£, thousands) - headings problem revisited | Table: `b_64`, Intro Prose: `b_63`, Atomic (Full) |

## 4. Chunk Content & Dual Representation Details
### Chunk 1: `b_1_atomic` (table)
- **Section**: `sample-tables.pdf > Design and build accessible PDF tables Sample tables`
- **Metadata**: `{'table_id': 'b_1', 'is_atomic': True, 'row_range': [0, 2], 'total_rows': 2, 'section_path': ['sample-tables.pdf', 'Design and build accessible PDF tables Sample tables'], 'preceding_prose_id': None, 'page_numbers': [1]}`

#### [A] Content for Vector Embedding (KV / Semantic Linearization):

```text
Section: sample-tables.pdf > Design and build accessible PDF tables Sample tables
Table Title: Table 1
Row 1: Column header (TH): Data cell (TD); Column header (TH): Data cell (TD); Column header (TH): Row header (TH)
Row 2: Column header (TH): Data cell (TD); Column header (TH): Data cell (TD); Column header (TH): Row header(TH)
```

#### [B] Content for LLM Context Generation:

**Table 1**

| Column header (TH) | Column header (TH) | Column header (TH) |
| --- | --- | --- |
| Data cell (TD) | Data cell (TD) | Row header (TH) |
| Data cell (TD) | Data cell (TD) | Row header(TH) |

---

### Chunk 2: `b_2` (paragraph)
- **Section**: `sample-tables.pdf > Design and build accessible PDF tables Sample tables`
- **Metadata**: `{'section_path': ['sample-tables.pdf', 'Design and build accessible PDF tables Sample tables'], 'parent_id': 'b_0', 'level': 0, 'page': 1}`

#### [A] Content for Vector Embedding (KV / Semantic Linearization):

```text
[sample-tables.pdf > Design and build accessible PDF tables Sample tables]
Table 1
```

#### [B] Content for LLM Context Generation:

> Table 1

---

### Chunk 3: `b_3_atomic` (table)
- **Section**: `sample-tables.pdf > Design and build accessible PDF tables Sample tables`
- **Metadata**: `{'table_id': 'b_3', 'is_atomic': True, 'row_range': [0, 7], 'total_rows': 7, 'section_path': ['sample-tables.pdf', 'Design and build accessible PDF tables Sample tables'], 'preceding_prose_id': 'b_2', 'page_numbers': [1]}`

#### [A] Content for Vector Embedding (KV / Semantic Linearization):

```text
Section: sample-tables.pdf > Design and build accessible PDF tables Sample tables
Table Title: Table 2: example of footnotes referenced from within a table
Row 1: Expenditure by function £ million: Policy functions; Expenditure by function £ million: Financial; 2009/10: 22.5; 2010/11 1: 30.57
Row 2: Expenditure by function £ million: Information 2; 2009/10: 10.2; 2010/11 1: 14.8
Row 3: Expenditure by function £ million: Contingency; 2009/10: 2.6; 2010/11 1: 1.2
Row 4: Expenditure by function £ million: Remunerated functions; Expenditure by function £ million: Agency services 3; 2009/10: 44.7; 2010/11 1: 35.91
Row 5: Expenditure by function £ million: Payments; 2009/10: 22.41; 2010/11 1: 19.88
Row 6: Expenditure by function £ million: Banking; 2009/10: 22.90; 2010/11 1: 44.23
Row 7: Expendi
... [truncated]
```

#### [B] Content for LLM Context Generation:

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

---

### Chunk 4: `b_4` (paragraph)
- **Section**: `sample-tables.pdf > Design and build accessible PDF tables Sample tables`
- **Metadata**: `{'section_path': ['sample-tables.pdf', 'Design and build accessible PDF tables Sample tables'], 'parent_id': 'b_0', 'level': 0, 'page': 1}`

#### [A] Content for Vector Embedding (KV / Semantic Linearization):

```text
[sample-tables.pdf > Design and build accessible PDF tables Sample tables]
Table 2: example of footnotes referenced from within a table
```

#### [B] Content for LLM Context Generation:

> Table 2: example of footnotes referenced from within a table

---

### Chunk 5: `b_5` (paragraph)
- **Section**: `sample-tables.pdf > Design and build accessible PDF tables Sample tables`
- **Metadata**: `{'section_path': ['sample-tables.pdf', 'Design and build accessible PDF tables Sample tables'], 'parent_id': 'b_0', 'level': 0, 'page': 1}`

#### [A] Content for Vector Embedding (KV / Semantic Linearization):

```text
[sample-tables.pdf > Design and build accessible PDF tables Sample tables]
Provisional total as of publication date.
```

#### [B] Content for LLM Context Generation:

> Provisional total as of publication date.

---

### Chunk 6: `b_6` (paragraph)
- **Section**: `sample-tables.pdf > Design and build accessible PDF tables Sample tables`
- **Metadata**: `{'section_path': ['sample-tables.pdf', 'Design and build accessible PDF tables Sample tables'], 'parent_id': 'b_0', 'level': 0, 'page': 1}`

#### [A] Content for Vector Embedding (KV / Semantic Linearization):

```text
[sample-tables.pdf > Design and build accessible PDF tables Sample tables]
Costs associated with on-going information programmes.
```

#### [B] Content for LLM Context Generation:

> Costs associated with on-going information programmes.

---

### Chunk 7: `b_7` (paragraph)
- **Section**: `sample-tables.pdf > Design and build accessible PDF tables Sample tables`
- **Metadata**: `{'section_path': ['sample-tables.pdf', 'Design and build accessible PDF tables Sample tables'], 'parent_id': 'b_0', 'level': 0, 'page': 1}`

#### [A] Content for Vector Embedding (KV / Semantic Linearization):

```text
[sample-tables.pdf > Design and build accessible PDF tables Sample tables]
From the management accounts, net of recoveries, including interest charges.
```

#### [B] Content for LLM Context Generation:

> From the management accounts, net of recoveries, including interest charges.

---

### Chunk 8: `b_8_atomic` (table)
- **Section**: `sample-tables.pdf > Design and build accessible PDF tables Sample tables`
- **Metadata**: `{'table_id': 'b_8', 'is_atomic': True, 'row_range': [0, 5], 'total_rows': 5, 'section_path': ['sample-tables.pdf', 'Design and build accessible PDF tables Sample tables'], 'preceding_prose_id': 'b_7', 'page_numbers': [1]}`

#### [A] Content for Vector Embedding (KV / Semantic Linearization):

```text
Section: sample-tables.pdf > Design and build accessible PDF tables Sample tables
Table Title: Table 3: "film credits" style layout
Row 1: Main character: Rupert Grint; Daniel Radcliffe: Sidekick 1
Row 2: Main character: Emma Watson; Daniel Radcliffe: Sidekick 2
Row 3: Main character: Robbie Coltrane; Daniel Radcliffe: Lovable ogre
Row 4: Main character: Maggie Smith; Daniel Radcliffe: Professor
Row 5: Main character: Richard Harris; Daniel Radcliffe: Headmaster
```

#### [B] Content for LLM Context Generation:

**Table 3: "film credits" style layout**

| Main character | Daniel Radcliffe |
| --- | --- |
| Rupert Grint | Sidekick 1 |
| Emma Watson | Sidekick 2 |
| Robbie Coltrane | Lovable ogre |
| Maggie Smith | Professor |
| Richard Harris | Headmaster |

---

### Chunk 9: `b_9` (paragraph)
- **Section**: `sample-tables.pdf > Design and build accessible PDF tables Sample tables`
- **Metadata**: `{'section_path': ['sample-tables.pdf', 'Design and build accessible PDF tables Sample tables'], 'parent_id': 'b_0', 'level': 0, 'page': 1}`

#### [A] Content for Vector Embedding (KV / Semantic Linearization):

```text
[sample-tables.pdf > Design and build accessible PDF tables Sample tables]
Table 3: "film credits" style layout
```

#### [B] Content for LLM Context Generation:

> Table 3: "film credits" style layout

---

### Chunk 10: `b_10` (paragraph)
- **Section**: `sample-tables.pdf > Design and build accessible PDF tables Sample tables`
- **Metadata**: `{'section_path': ['sample-tables.pdf', 'Design and build accessible PDF tables Sample tables'], 'parent_id': 'b_0', 'level': 0, 'page': 1}`

#### [A] Content for Vector Embedding (KV / Semantic Linearization):

```text
[sample-tables.pdf > Design and build accessible PDF tables Sample tables]
Table 4: table 3 with column headers added
```

#### [B] Content for LLM Context Generation:

> Table 4: table 3 with column headers added

---

### Chunk 11: `b_11_atomic` (table)
- **Section**: `sample-tables.pdf > Design and build accessible PDF tables Sample tables`
- **Metadata**: `{'table_id': 'b_11', 'is_atomic': True, 'row_range': [0, 6], 'total_rows': 6, 'section_path': ['sample-tables.pdf', 'Design and build accessible PDF tables Sample tables'], 'preceding_prose_id': 'b_10', 'page_numbers': [2]}`

#### [A] Content for Vector Embedding (KV / Semantic Linearization):

```text
Section: sample-tables.pdf > Design and build accessible PDF tables Sample tables
Row 1: Role: Daniel Radcliffe; Actor: Main character
Row 2: Role: Rupert Grint; Actor: Sidekick 1
Row 3: Role: Emma Watson; Actor: Sidekick 2
Row 4: Role: Robbie Coltrane; Actor: Lovable ogre
Row 5: Role: Maggie Smith; Actor: Professor
Row 6: Role: Richard Harris; Actor: Headmaster
```

#### [B] Content for LLM Context Generation:

| Role | Actor |
| --- | --- |
| Daniel Radcliffe | Main character |
| Rupert Grint | Sidekick 1 |
| Emma Watson | Sidekick 2 |
| Robbie Coltrane | Lovable ogre |
| Maggie Smith | Professor |
| Richard Harris | Headmaster |

---

### Chunk 12: `b_12` (paragraph)
- **Section**: `sample-tables.pdf > Design and build accessible PDF tables Sample tables`
- **Metadata**: `{'section_path': ['sample-tables.pdf', 'Design and build accessible PDF tables Sample tables'], 'parent_id': 'b_0', 'level': 0, 'page': 1}`

#### [A] Content for Vector Embedding (KV / Semantic Linearization):

```text
[sample-tables.pdf > Design and build accessible PDF tables Sample tables]
Table 5: year-end financial statement (£, thousands)
```

#### [B] Content for LLM Context Generation:

> Table 5: year-end financial statement (£, thousands)

---

### Chunk 13: `b_13_atomic` (table)
- **Section**: `sample-tables.pdf > Design and build accessible PDF tables Sample tables`
- **Metadata**: `{'table_id': 'b_13', 'is_atomic': True, 'row_range': [0, 8], 'total_rows': 8, 'section_path': ['sample-tables.pdf', 'Design and build accessible PDF tables Sample tables'], 'preceding_prose_id': 'b_12', 'page_numbers': [2]}`

#### [A] Content for Vector Embedding (KV / Semantic Linearization):

```text
Section: sample-tables.pdf > Design and build accessible PDF tables Sample tables
Row 1: : Non-current assets
Row 2: : Property; 2010: 345; 2009: 445; 2008: 222
Row 3: : Investment; 2010: 567; 2009: 654; 2008: 423
Row 4: : Intangibles; 2010: 423; 2009: 123; 2008: 453
Row 5: : Current assets
Row 6: : Trade and other receivables; 2010: 435; 2009: 634; 2008: 231
Row 7: : Cash and cash equivalents; 2010: 524; 2009: 123; 2008: 482
Row 8: : Other; 2010: 223; 2009: 211; 2008: 254
```

#### [B] Content for LLM Context Generation:

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

---

### Chunk 14: `b_14` (paragraph)
- **Section**: `sample-tables.pdf > Design and build accessible PDF tables Sample tables`
- **Metadata**: `{'section_path': ['sample-tables.pdf', 'Design and build accessible PDF tables Sample tables'], 'parent_id': 'b_0', 'level': 0, 'page': 1}`

#### [A] Content for Vector Embedding (KV / Semantic Linearization):

```text
[sample-tables.pdf > Design and build accessible PDF tables Sample tables]
Table 6: a table with a more serious headings problem Table 7: year-end statement, non-current assets (£, thousands)
```

#### [B] Content for LLM Context Generation:

> Table 6: a table with a more serious headings problem Table 7: year-end statement, non-current assets (£, thousands)

---

### Chunk 15: `b_15_atomic` (table)
- **Section**: `sample-tables.pdf > Design and build accessible PDF tables Sample tables`
- **Metadata**: `{'table_id': 'b_15', 'is_atomic': True, 'row_range': [0, 8], 'total_rows': 8, 'section_path': ['sample-tables.pdf', 'Design and build accessible PDF tables Sample tables'], 'preceding_prose_id': 'b_14', 'page_numbers': [2]}`

#### [A] Content for Vector Embedding (KV / Semantic Linearization):

```text
Section: sample-tables.pdf > Design and build accessible PDF tables Sample tables
Row 1: Rainfall (inches): 2010; Americas: 2010; Asia: 2010; Europe: 2010; Africa: 2010
Row 2: Rainfall (inches): Average; Americas: 104; Asia: 201; Europe: 193; Africa: 144
Row 3: Rainfall (inches): 24 hour high; Americas: 15; Asia: 26; Europe: 27; Africa: 18
Row 4: Rainfall (inches): 12 hour high; Americas: 9; Asia: 10; Europe: 11; Africa: 12
Row 5: Rainfall (inches): 2009; Americas: 2009; Asia: 2009; Europe: 2009; Africa: 2009
Row 6: Rainfall (inches): Average; Americas: 133; Asia: 244; Europe: 155; Africa: 166
Row 7: Rainfall (inches): 24 hour high; Americas: 27; Asia: 28; Europe: 29; Africa: 20
Row 8: Rainfall (inches): 12 hour high; Americas: 11; Asia: 12; Europe: 13; Africa: 16
```

#### [B] Content for LLM Context Generation:

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

---

### Chunk 16: `b_16_atomic` (table)
- **Section**: `sample-tables.pdf > Design and build accessible PDF tables Sample tables`
- **Metadata**: `{'table_id': 'b_16', 'is_atomic': True, 'row_range': [0, 3], 'total_rows': 3, 'section_path': ['sample-tables.pdf', 'Design and build accessible PDF tables Sample tables'], 'preceding_prose_id': 'b_14', 'page_numbers': [3]}`

#### [A] Content for Vector Embedding (KV / Semantic Linearization):

```text
Section: sample-tables.pdf > Design and build accessible PDF tables Sample tables
Row 1: Non-current assets: Property; 2010: 345; 2009: 445; 2008: 222
Row 2: Non-current assets: Investment; 2010: 567; 2009: 654; 2008: 423
Row 3: Non-current assets: Intangibles; 2010: 423; 2009: 123; 2008: 453
```

#### [B] Content for LLM Context Generation:

| Non-current assets | 2010 | 2009 | 2008 |
| --- | --- | --- | --- |
| Property | 345 | 445 | 222 |
| Investment | 567 | 654 | 423 |
| Intangibles | 423 | 123 | 453 |

---

### Chunk 17: `b_17` (paragraph)
- **Section**: `sample-tables.pdf > Design and build accessible PDF tables Sample tables`
- **Metadata**: `{'section_path': ['sample-tables.pdf', 'Design and build accessible PDF tables Sample tables'], 'parent_id': 'b_0', 'level': 0, 'page': 1}`

#### [A] Content for Vector Embedding (KV / Semantic Linearization):

```text
[sample-tables.pdf > Design and build accessible PDF tables Sample tables]
Table 8: year-end statement, current assets (£, thousands)
```

#### [B] Content for LLM Context Generation:

> Table 8: year-end statement, current assets (£, thousands)

---

### Chunk 18: `b_18_atomic` (table)
- **Section**: `sample-tables.pdf > Design and build accessible PDF tables Sample tables`
- **Metadata**: `{'table_id': 'b_18', 'is_atomic': True, 'row_range': [0, 3], 'total_rows': 3, 'section_path': ['sample-tables.pdf', 'Design and build accessible PDF tables Sample tables'], 'preceding_prose_id': 'b_17', 'page_numbers': [3]}`

#### [A] Content for Vector Embedding (KV / Semantic Linearization):

```text
Section: sample-tables.pdf > Design and build accessible PDF tables Sample tables
Row 1: Current assets: 435; 2009: 634; 2008: Trade and other receivables 231
Row 2: Current assets: Cash and cash equivalents 524; 2009: 123; 2008: 482
Row 3: Current assets: Other; 2010: 223; 2009: 211; 2008: 254
```

#### [B] Content for LLM Context Generation:

| Current assets | 2010 | 2009 | 2008 |
| --- | --- | --- | --- |
| 435 |  | 634 | Trade and other receivables 231 |
| Cash and cash equivalents 524 |  | 123 | 482 |
| Other | 223 | 211 | 254 |

---

### Chunk 19: `b_19` (paragraph)
- **Section**: `sample-tables.pdf > Design and build accessible PDF tables Sample tables`
- **Metadata**: `{'section_path': ['sample-tables.pdf', 'Design and build accessible PDF tables Sample tables'], 'parent_id': 'b_0', 'level': 0, 'page': 1}`

#### [A] Content for Vector Embedding (KV / Semantic Linearization):

```text
[sample-tables.pdf > Design and build accessible PDF tables Sample tables]
Table 9: rainfall by continent, 2009
```

#### [B] Content for LLM Context Generation:

> Table 9: rainfall by continent, 2009

---

### Chunk 20: `b_20_atomic` (table)
- **Section**: `sample-tables.pdf > Design and build accessible PDF tables Sample tables`
- **Metadata**: `{'table_id': 'b_20', 'is_atomic': True, 'row_range': [0, 3], 'total_rows': 3, 'section_path': ['sample-tables.pdf', 'Design and build accessible PDF tables Sample tables'], 'preceding_prose_id': 'b_19', 'page_numbers': [3]}`

#### [A] Content for Vector Embedding (KV / Semantic Linearization):

```text
Section: sample-tables.pdf > Design and build accessible PDF tables Sample tables
Row 1: Rainfall (inches): Average; Americas: 133 244; Europe: 155; Africa: 166
Row 2: Rainfall (inches): 24 hour high; Americas: 27; Asia: 28; Europe: 29; Africa: 20
Row 3: Rainfall (inches): 12 hour high; Americas: 11; Asia: 12; Europe: 13; Africa: 16
```

#### [B] Content for LLM Context Generation:

| Rainfall (inches) | Americas | Asia | Europe | Africa |
| --- | --- | --- | --- | --- |
| Average | 133 244 |  | 155 | 166 |
| 24 hour high | 27 | 28 | 29 | 20 |
| 12 hour high | 11 | 12 | 13 | 16 |

---

### Chunk 21: `b_21_atomic` (table)
- **Section**: `sample-tables.pdf > Design and build accessible PDF tables Sample tables`
- **Metadata**: `{'table_id': 'b_21', 'is_atomic': True, 'row_range': [0, 13], 'total_rows': 13, 'section_path': ['sample-tables.pdf', 'Design and build accessible PDF tables Sample tables'], 'preceding_prose_id': 'b_19', 'page_numbers': [4]}`

#### [A] Content for Vector Embedding (KV / Semantic Linearization):

```text
Section: sample-tables.pdf > Design and build accessible PDF tables Sample tables
Table Title: Table 10: self-contained year-end statement (£, thousands) (multiple layout problems)
Row 1: : General income; 2011: 250,000; 2010 restated: 200,000
Row 2: : Increase in value, WIP; 2011: 15,000; 2010 restated: 30,000
Row 3: 2011: 265,000; 2010 restated: 230,000
Row 4: : Administrative costs
Row 5: : Staff costs; 2011: (200,000); 2010 restated: (150,000)
Row 6: : Early departures; 2011: (10,000); 2010 restated: (20,000)
Row 7: : Other; 2011: (25,000); 2010 restated: (10,000)
Row 8: : Depreciation; 2011: (10,000); 2010 restated: (10,000)
Row 9: : Programme costs
Row 10: : Impairment loss; 2011: (10,000); 2010 restated: (5,000)
Row 11: : Other; 2011: (5,000); 2010 restated: (5,000)
Row 12: 2011: (2
... [truncated]
```

#### [B] Content for LLM Context Generation:

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
| Depreciation | (10,000) |  | (10,000) |  |
| Programme costs |  |  |  |  |
| Impairment loss | (10,000) |  | (5,000) |  |
| Other | (5,000) |  | (5,000) |  |
|  | (260,000) |  | (200,000) |  |
| Surplus |  | 5,000 |  | 30,000 |

---

### Chunk 22: `b_22` (paragraph)
- **Section**: `sample-tables.pdf > Design and build accessible PDF tables Sample tables`
- **Metadata**: `{'section_path': ['sample-tables.pdf', 'Design and build accessible PDF tables Sample tables'], 'parent_id': 'b_0', 'level': 0, 'page': 1}`

#### [A] Content for Vector Embedding (KV / Semantic Linearization):

```text
[sample-tables.pdf > Design and build accessible PDF tables Sample tables]
Table 10: self-contained year-end statement (£, thousands) (multiple layout problems)
```

#### [B] Content for LLM Context Generation:

> Table 10: self-contained year-end statement (£, thousands) (multiple layout problems)

---

### Chunk 23: `b_23_atomic` (table)
- **Section**: `sample-tables.pdf > Design and build accessible PDF tables Sample tables`
- **Metadata**: `{'table_id': 'b_23', 'is_atomic': True, 'row_range': [0, 11], 'total_rows': 11, 'section_path': ['sample-tables.pdf', 'Design and build accessible PDF tables Sample tables'], 'preceding_prose_id': 'b_22', 'page_numbers': [4]}`

#### [A] Content for Vector Embedding (KV / Semantic Linearization):

```text
Section: sample-tables.pdf > Design and build accessible PDF tables Sample tables
Table Title: Table 11: self-contained year-end statement (£, thousands) (multiple problems resolved)
Row 1: : Income; : General income; 2011: 250,000; 2010 restated: 200,000
Row 2: : Increase in value; 2011: 15,000; 2010 restated: 30,000
Row 3: : Total income; 2011: 265,000; 2010 restated: 230,000
Row 4: : Administrative costs; : Staff costs; 2011: (200,000); 2010 restated: (150,000)
Row 5: : Early departures; 2011: (10,000); 2010 restated: (20,000)
Row 6: : Other operating costs; 2011: (25,000); 2010 restated: (10,000)
Row 7: : Depreciation; 2011: (10,000); 2010 restated: (10,000)
Row 8: : Programme costs; : Impairment loss; 2011: (10,000); 2010 restated: (5,000)
Row 9: : Other; 2011: (5,000); 2010 restated:
... [truncated]
```

#### [B] Content for LLM Context Generation:

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
| Programme costs | Impairment loss | (10,000) | (5,000) |
|  | Other | (5,000) | (5,000) |
|  | Total costs | (260,000) | (200,000) |
| Surplus | Surplus | 5,000 | 30,000 |

---

### Chunk 24: `b_24` (paragraph)
- **Section**: `sample-tables.pdf > Design and build accessible PDF tables Sample tables`
- **Metadata**: `{'section_path': ['sample-tables.pdf', 'Design and build accessible PDF tables Sample tables'], 'parent_id': 'b_0', 'level': 0, 'page': 1}`

#### [A] Content for Vector Embedding (KV / Semantic Linearization):

```text
[sample-tables.pdf > Design and build accessible PDF tables Sample tables]
Table 11: self-contained year-end statement (£, thousands) (multiple problems resolved)
```

#### [B] Content for LLM Context Generation:

> Table 11: self-contained year-end statement (£, thousands) (multiple problems resolved)

---

### Chunk 25: `b_25_atomic` (table)
- **Section**: `sample-tables.pdf > Design and build accessible PDF tables Sample tables`
- **Metadata**: `{'table_id': 'b_25', 'is_atomic': True, 'row_range': [0, 3], 'total_rows': 3, 'section_path': ['sample-tables.pdf', 'Design and build accessible PDF tables Sample tables'], 'preceding_prose_id': 'b_24', 'page_numbers': [5]}`

#### [A] Content for Vector Embedding (KV / Semantic Linearization):

```text
Section: sample-tables.pdf > Design and build accessible PDF tables Sample tables
Table Title: Table 12: merged data cells are not recommended
Row 1: Name: Bob; 2008.Yes: 2; 2008.No: 5; 2009.Yes: 6; 2009.No: 7
Row 2: Name: Sue; 2008.Yes: 3; 2008.No: 8; 2009.Yes: 4; 2009.No: 7
Row 3: Name: Sam; 2008.Yes: [data relating to both columns in a single cell spanning both]; 2008.No: [data relating to both columns in a single cell spanning both]; 2009.Yes: [data relating to single cell; 2009.No: both columns in both]
```

#### [B] Content for LLM Context Generation:

**Table 12: merged data cells are not recommended**

| Name | 2008.Yes | 2008.No | 2009.Yes | 2009.No |
| --- | --- | --- | --- | --- |
| Bob | 2 | 5 | 6 | 7 |
| Sue | 3 | 8 | 4 | 7 |
| Sam | [data relating to both columns in a single cell spanning both] | [data relating to both columns in a single cell spanning both] | [data relating to single cell | both columns in both] |

---

### Chunk 26: `b_26` (paragraph)
- **Section**: `sample-tables.pdf > Design and build accessible PDF tables Sample tables`
- **Metadata**: `{'section_path': ['sample-tables.pdf', 'Design and build accessible PDF tables Sample tables'], 'parent_id': 'b_0', 'level': 0, 'page': 1}`

#### [A] Content for Vector Embedding (KV / Semantic Linearization):

```text
[sample-tables.pdf > Design and build accessible PDF tables Sample tables]
Table 12: merged data cells are not recommended
```

#### [B] Content for LLM Context Generation:

> Table 12: merged data cells are not recommended

---

### Chunk 27: `b_27_atomic` (table)
- **Section**: `sample-tables.pdf > Design and build accessible PDF tables Sample tables`
- **Metadata**: `{'table_id': 'b_27', 'is_atomic': True, 'row_range': [0, 3], 'total_rows': 3, 'section_path': ['sample-tables.pdf', 'Design and build accessible PDF tables Sample tables'], 'preceding_prose_id': 'b_26', 'page_numbers': [5]}`

#### [A] Content for Vector Embedding (KV / Semantic Linearization):

```text
Section: sample-tables.pdf > Design and build accessible PDF tables Sample tables
Table Title: Table 13: use of graphic symbols
Row 1: Question: Are you a UK citizen? ; Respondent B: ; Respondent C: 
Row 2: Question: Are you currently employed?; Respondent A: ; Respondent B: ; Respondent C: 
Row 3: Question: Do you have a driving licence?; Respondent A: ; Respondent B: ; Respondent C: 
```

#### [B] Content for LLM Context Generation:

**Table 13: use of graphic symbols**

| Question | Respondent A | Respondent B | Respondent C |
| --- | --- | --- | --- |
| Are you a UK citizen?  |  |  |  |
| Are you currently employed? |  |  |  |
| Do you have a driving licence? |  |  |  |

---

### Chunk 28: `b_28` (paragraph)
- **Section**: `sample-tables.pdf > Design and build accessible PDF tables Sample tables`
- **Metadata**: `{'section_path': ['sample-tables.pdf', 'Design and build accessible PDF tables Sample tables'], 'parent_id': 'b_0', 'level': 0, 'page': 1}`

#### [A] Content for Vector Embedding (KV / Semantic Linearization):

```text
[sample-tables.pdf > Design and build accessible PDF tables Sample tables]
Table 13: use of graphic symbols
```

#### [B] Content for LLM Context Generation:

> Table 13: use of graphic symbols

---

### Chunk 29: `b_29_atomic` (table)
- **Section**: `sample-tables.pdf > Design and build accessible PDF tables Sample tables`
- **Metadata**: `{'table_id': 'b_29', 'is_atomic': True, 'row_range': [0, 3], 'total_rows': 3, 'section_path': ['sample-tables.pdf', 'Design and build accessible PDF tables Sample tables'], 'preceding_prose_id': 'b_28', 'page_numbers': [5]}`

#### [A] Content for Vector Embedding (KV / Semantic Linearization):

```text
Section: sample-tables.pdf > Design and build accessible PDF tables Sample tables
Table Title: Table 14: symbols replaced by real text
Row 1: Question: No; Respondent A: Yes; Respondent B: No; Respondent C: Are you a UK citizen?
Row 2: Question: Yes; Respondent A: No; Respondent B: Yes; Respondent C: Are you currently employed?
Row 3: Question: No; Respondent B: No Yes; Respondent C: Do you have a driving licence?
```

#### [B] Content for LLM Context Generation:

**Table 14: symbols replaced by real text**

| Question | Respondent A | Respondent B | Respondent C |
| --- | --- | --- | --- |
| No | Yes | No | Are you a UK citizen? |
| Yes | No | Yes | Are you currently employed? |
| No |  | No Yes | Do you have a driving licence? |

---

### Chunk 30: `b_30` (paragraph)
- **Section**: `sample-tables.pdf > Design and build accessible PDF tables Sample tables`
- **Metadata**: `{'section_path': ['sample-tables.pdf', 'Design and build accessible PDF tables Sample tables'], 'parent_id': 'b_0', 'level': 0, 'page': 1}`

#### [A] Content for Vector Embedding (KV / Semantic Linearization):

```text
[sample-tables.pdf > Design and build accessible PDF tables Sample tables]
Table 14: symbols replaced by real text
```

#### [B] Content for LLM Context Generation:

> Table 14: symbols replaced by real text

---

### Chunk 31: `b_31_atomic` (table)
- **Section**: `sample-tables.pdf > Design and build accessible PDF tables Sample tables`
- **Metadata**: `{'table_id': 'b_31', 'is_atomic': True, 'row_range': [0, 6], 'total_rows': 6, 'section_path': ['sample-tables.pdf', 'Design and build accessible PDF tables Sample tables'], 'preceding_prose_id': 'b_30', 'page_numbers': [5]}`

#### [A] Content for Vector Embedding (KV / Semantic Linearization):

```text
Section: sample-tables.pdf > Design and build accessible PDF tables Sample tables
Table Title: Table 15: courses offered by Institution X. A = Bachelor of Science, B = Bachelor of Arts, C = Masters, D = Doctorate, E = Diploma
Row 1: : Economics; 2006: A, B; 2007: A, C; 2008: A, B; 2009: A, C
Row 2: : International relations; 2006: A, E; 2007: A, E; 2008: A, B; 2009: A, E
Row 3: : Philosophy; 2006: A; 2007: A; 2008: A; 2009: A, D
Row 4: : Politics; 2006: A, D; 2007: A, D; 2008: A, D; 2009: A
Row 5: : Mathematics; 2006: B, C; 2007: B; 2008: A, E; 2009: A, B
Row 6: : English; 2006: A, C; 2007: A, B; 2008: A,B; 2009: C
```

#### [B] Content for LLM Context Generation:

**Table 15: courses offered by Institution X. A = Bachelor of Science, B = Bachelor of Arts, C = Masters, D = Doctorate, E = Diploma**

|  | 2006 | 2007 | 2008 | 2009 |
| --- | --- | --- | --- | --- |
| Economics | A, B | A, C | A, B | A, C |
| International relations | A, E | A, E | A, B | A, E |
| Philosophy | A | A | A | A, D |
| Politics | A, D | A, D | A, D | A |
| Mathematics | B, C | B | A, E | A, B |
| English | A, C | A, B | A,B | C |

---

### Chunk 32: `b_32` (paragraph)
- **Section**: `sample-tables.pdf > Design and build accessible PDF tables Sample tables`
- **Metadata**: `{'section_path': ['sample-tables.pdf', 'Design and build accessible PDF tables Sample tables'], 'parent_id': 'b_0', 'level': 0, 'page': 1}`

#### [A] Content for Vector Embedding (KV / Semantic Linearization):

```text
[sample-tables.pdf > Design and build accessible PDF tables Sample tables]
Table 15: courses offered by Institution X. A = Bachelor of Science, B = Bachelor of Arts, C = Masters, D = Doctorate, E = Diploma
```

#### [B] Content for LLM Context Generation:

> Table 15: courses offered by Institution X. A = Bachelor of Science, B = Bachelor of Arts, C = Masters, D = Doctorate, E = Diploma

---

### Chunk 33: `b_33_atomic` (table)
- **Section**: `sample-tables.pdf > Design and build accessible PDF tables Sample tables`
- **Metadata**: `{'table_id': 'b_33', 'is_atomic': True, 'row_range': [0, 6], 'total_rows': 6, 'section_path': ['sample-tables.pdf', 'Design and build accessible PDF tables Sample tables'], 'preceding_prose_id': 'b_32', 'page_numbers': [6]}`

#### [A] Content for Vector Embedding (KV / Semantic Linearization):

```text
Section: sample-tables.pdf > Design and build accessible PDF tables Sample tables
Table Title: Table 16: Masters courses offered by Institution X
Row 1: : Economics; 2006: No; 2007: Yes; 2008: Yes; 2009: Yes
Row 2: : International relations; 2006: No; 2007: No; 2008: No; 2009: No
Row 3: : Philosophy; 2006: No; 2007: No; 2008: No; 2009: No
Row 4: : Politics; 2006: No; 2007: No; 2008: No; 2009: No
Row 5: : Mathematics; 2006: Yes; 2007: No; 2008: No; 2009: No
Row 6: : English; 2006: Yes; 2007: Yes; 2008: Yes; 2009: Yes
```

#### [B] Content for LLM Context Generation:

**Table 16: Masters courses offered by Institution X**

|  | 2006 | 2007 | 2008 | 2009 |
| --- | --- | --- | --- | --- |
| Economics | No | Yes | Yes | Yes |
| International relations | No | No | No | No |
| Philosophy | No | No | No | No |
| Politics | No | No | No | No |
| Mathematics | Yes | No | No | No |
| English | Yes | Yes | Yes | Yes |

---

### Chunk 34: `b_34` (paragraph)
- **Section**: `sample-tables.pdf > Design and build accessible PDF tables Sample tables`
- **Metadata**: `{'section_path': ['sample-tables.pdf', 'Design and build accessible PDF tables Sample tables'], 'parent_id': 'b_0', 'level': 0, 'page': 1}`

#### [A] Content for Vector Embedding (KV / Semantic Linearization):

```text
[sample-tables.pdf > Design and build accessible PDF tables Sample tables]
Table 16: Masters courses offered by Institution X
```

#### [B] Content for LLM Context Generation:

> Table 16: Masters courses offered by Institution X

---

### Chunk 35: `b_35_atomic` (table)
- **Section**: `sample-tables.pdf > Design and build accessible PDF tables Sample tables`
- **Metadata**: `{'table_id': 'b_35', 'is_atomic': True, 'row_range': [0, 10], 'total_rows': 10, 'section_path': ['sample-tables.pdf', 'Design and build accessible PDF tables Sample tables'], 'preceding_prose_id': 'b_34', 'page_numbers': [6]}`

#### [A] Content for Vector Embedding (KV / Semantic Linearization):

```text
Section: sample-tables.pdf > Design and build accessible PDF tables Sample tables
Table Title: Table 17: accounts, 2011 (£, thousands)
Row 1: Accounting item: Income General income; 2011: 200,000
Row 2: Accounting item: Increase in value, WIP; 2011: 30,000
Row 3: Accounting item: Income subtotal; 2011: 230,000
Row 4: Accounting item: Administrative costs Staff; 2011: 150,000
Row 5: Accounting item: Early departures; 2011: 20,000
Row 6: Accounting item: Other operating costs; 2011: 10,000
Row 7: Accounting item: Depreciation; 2011: 10,000
Row 8: Accounting item: Programme costs Impairment loss; 2011: 10,000
Row 9: Accounting item: Costs subtotal; 2011: 200,000
Row 10: Accounting item: Balance; 2011: 30,000
```

#### [B] Content for LLM Context Generation:

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

---

### Chunk 36: `b_36` (paragraph)
- **Section**: `sample-tables.pdf > Design and build accessible PDF tables Sample tables`
- **Metadata**: `{'section_path': ['sample-tables.pdf', 'Design and build accessible PDF tables Sample tables'], 'parent_id': 'b_0', 'level': 0, 'page': 1}`

#### [A] Content for Vector Embedding (KV / Semantic Linearization):

```text
[sample-tables.pdf > Design and build accessible PDF tables Sample tables]
Table 17: accounts, 2011 (£, thousands)
```

#### [B] Content for LLM Context Generation:

> Table 17: accounts, 2011 (£, thousands)

---

### Chunk 37: `b_37_atomic` (table)
- **Section**: `sample-tables.pdf > Design and build accessible PDF tables Sample tables`
- **Metadata**: `{'table_id': 'b_37', 'is_atomic': True, 'row_range': [0, 10], 'total_rows': 10, 'section_path': ['sample-tables.pdf', 'Design and build accessible PDF tables Sample tables'], 'preceding_prose_id': 'b_36', 'page_numbers': [6]}`

#### [A] Content for Vector Embedding (KV / Semantic Linearization):

```text
Section: sample-tables.pdf > Design and build accessible PDF tables Sample tables
Table Title: Table 18: accounts, 2011 (£, thousands)
Row 1: Accounting item: Income; Accounting item: General income; 2011: 200,000
Row 2: Accounting item: Increase in value, WIP; 2011: 30,000
Row 3: Accounting item: Income subtotal; 2011: 230,000
Row 4: Accounting item: Administrative costs; Accounting item: Staff; 2011: (150,000)
Row 5: Accounting item: Early departures; 2011: (20,000)
Row 6: Accounting item: Other operating costs; 2011: (10,000)
Row 7: Accounting item: Depreciation; 2011: (10,000)
Row 8: Accounting item: Programme costs; Accounting item: Impairment loss; 2011: (10,000)
Row 9: Accounting item: Costs subtotal; 2011: (200,000)
Row 10: Accounting item: Balance; Accounting item: Balance; 2011: 
... [truncated]
```

#### [B] Content for LLM Context Generation:

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

---

### Chunk 38: `b_38` (paragraph)
- **Section**: `sample-tables.pdf > Design and build accessible PDF tables Sample tables`
- **Metadata**: `{'section_path': ['sample-tables.pdf', 'Design and build accessible PDF tables Sample tables'], 'parent_id': 'b_0', 'level': 0, 'page': 1}`

#### [A] Content for Vector Embedding (KV / Semantic Linearization):

```text
[sample-tables.pdf > Design and build accessible PDF tables Sample tables]
Table 18: accounts, 2011 (£, thousands)
```

#### [B] Content for LLM Context Generation:

> Table 18: accounts, 2011 (£, thousands)

---

### Chunk 39: `b_39` (paragraph)
- **Section**: `sample-tables.pdf > Design and build accessible PDF tables Sample tables`
- **Metadata**: `{'section_path': ['sample-tables.pdf', 'Design and build accessible PDF tables Sample tables'], 'parent_id': 'b_0', 'level': 0, 'page': 1}`

#### [A] Content for Vector Embedding (KV / Semantic Linearization):

```text
[sample-tables.pdf > Design and build accessible PDF tables Sample tables]
Table 19: Human Development Index (HDI)
```

#### [B] Content for LLM Context Generation:

> Table 19: Human Development Index (HDI)

---

### Chunk 40: `b_41_atomic` (table)
- **Section**: `sample-tables.pdf > trends, 1980 to 2010. Source: Barro-Lee March, 2010`
- **Metadata**: `{'table_id': 'b_41', 'is_atomic': True, 'row_range': [0, 5], 'total_rows': 5, 'section_path': ['sample-tables.pdf', 'trends, 1980 to 2010. Source: Barro-Lee March, 2010'], 'preceding_prose_id': None, 'page_numbers': [7]}`

#### [A] Content for Vector Embedding (KV / Semantic Linearization):

```text
Section: sample-tables.pdf > trends, 1980 to 2010. Source: Barro-Lee March, 2010
Row 1: Country: Afghanistan; 1980: 0.78; 1990: 1.48; 2000: 2.16; 2010: 3.33
Row 2: Country: Albania; 1980: 8.89; 1990: 9.67; 2000: 9.89; 2010: 10.38
Row 3: Country: Algeria; 1980: 4.74; 1990: 3.33; 2000: 5.50; 2010: 7.24
Row 4: Country: Andorra; 1980: 4.98; 1990: 5.63; 2000: 9.09; 2010: 10.35
Row 5: Country: Angola; 1980: -; 1990: -; 2000: 4.42; 2010: 4.42
```

#### [B] Content for LLM Context Generation:

| Country | 1980 | 1990 | 2000 | 2010 |
| --- | --- | --- | --- | --- |
| Afghanistan | 0.78 | 1.48 | 2.16 | 3.33 |
| Albania | 8.89 | 9.67 | 9.89 | 10.38 |
| Algeria | 4.74 | 3.33 | 5.50 | 7.24 |
| Andorra | 4.98 | 5.63 | 9.09 | 10.35 |
| Angola | - | - | 4.42 | 4.42 |

---

### Chunk 41: `b_42_atomic` (table)
- **Section**: `sample-tables.pdf > trends, 1980 to 2010. Source: Barro-Lee March, 2010`
- **Metadata**: `{'table_id': 'b_42', 'is_atomic': True, 'row_range': [0, 7], 'total_rows': 7, 'section_path': ['sample-tables.pdf', 'trends, 1980 to 2010. Source: Barro-Lee March, 2010'], 'preceding_prose_id': None, 'page_numbers': [7]}`

#### [A] Content for Vector Embedding (KV / Semantic Linearization):

```text
Section: sample-tables.pdf > trends, 1980 to 2010. Source: Barro-Lee March, 2010
Table Title: Table 20: footnotes referenced from within a table
Row 1: Expenditure by function £million: Policy functions; Expenditure by function £million: Financial; 2009/10: 22.5; 2010/11 1: 30.57
Row 2: Expenditure by function £million: Policy functions; Expenditure by function £million: Information 2; 2009/10: 10.2; 2010/11 1: 14.8
Row 3: Expenditure by function £million: Policy functions; Expenditure by function £million: Contingency; 2009/10: 2.6; 2010/11 1: 1.2
Row 4: Expenditure by function £million: Remunerated functions; Expenditure by function £million: Agency services 3; 2009/10: 44.7; 2010/11 1: 35.91
Row 5: Expenditure by function £million: Remunerated functions; Expenditure by function £million
... [truncated]
```

#### [B] Content for LLM Context Generation:

**Table 20: footnotes referenced from within a table**

| Expenditure by function £million | Expenditure by function £million | 2009/10 | 2010/11 1 |
| --- | --- | --- | --- |
| Policy functions | Financial | 22.5 | 30.57 |
| Policy functions | Information 2 | 10.2 | 14.8 |
| Policy functions | Contingency | 2.6 | 1.2 |
| Remunerated functions | Agency services 3 | 44.7 | 35.91 |
| Remunerated functions | Payments | 22.41 | 19.88 |
| Remunerated functions | Banking | 22.90 | 44.23 |
| Remunerated functions | Other | 12.69 | 10.32 |

---

### Chunk 42: `b_43` (paragraph)
- **Section**: `sample-tables.pdf > trends, 1980 to 2010. Source: Barro-Lee March, 2010`
- **Metadata**: `{'section_path': ['sample-tables.pdf', 'trends, 1980 to 2010. Source: Barro-Lee March, 2010'], 'parent_id': 'b_40', 'level': 0, 'page': 1}`

#### [A] Content for Vector Embedding (KV / Semantic Linearization):

```text
[sample-tables.pdf > trends, 1980 to 2010. Source: Barro-Lee March, 2010]
Table 20: footnotes referenced from within a table
```

#### [B] Content for LLM Context Generation:

> Table 20: footnotes referenced from within a table

---

### Chunk 43: `b_44` (paragraph)
- **Section**: `sample-tables.pdf > trends, 1980 to 2010. Source: Barro-Lee March, 2010`
- **Metadata**: `{'section_path': ['sample-tables.pdf', 'trends, 1980 to 2010. Source: Barro-Lee March, 2010'], 'parent_id': 'b_40', 'level': 0, 'page': 1}`

#### [A] Content for Vector Embedding (KV / Semantic Linearization):

```text
[sample-tables.pdf > trends, 1980 to 2010. Source: Barro-Lee March, 2010]
Provisional total as of publication date.
```

#### [B] Content for LLM Context Generation:

> Provisional total as of publication date.

---

### Chunk 44: `b_45` (paragraph)
- **Section**: `sample-tables.pdf > trends, 1980 to 2010. Source: Barro-Lee March, 2010`
- **Metadata**: `{'section_path': ['sample-tables.pdf', 'trends, 1980 to 2010. Source: Barro-Lee March, 2010'], 'parent_id': 'b_40', 'level': 0, 'page': 1}`

#### [A] Content for Vector Embedding (KV / Semantic Linearization):

```text
[sample-tables.pdf > trends, 1980 to 2010. Source: Barro-Lee March, 2010]
Costs associated with on-going information programmes.
```

#### [B] Content for LLM Context Generation:

> Costs associated with on-going information programmes.

---

### Chunk 45: `b_46` (paragraph)
- **Section**: `sample-tables.pdf > trends, 1980 to 2010. Source: Barro-Lee March, 2010`
- **Metadata**: `{'section_path': ['sample-tables.pdf', 'trends, 1980 to 2010. Source: Barro-Lee March, 2010'], 'parent_id': 'b_40', 'level': 0, 'page': 1}`

#### [A] Content for Vector Embedding (KV / Semantic Linearization):

```text
[sample-tables.pdf > trends, 1980 to 2010. Source: Barro-Lee March, 2010]
From the management accounts, net of recoveries and including interest charges
```

#### [B] Content for LLM Context Generation:

> From the management accounts, net of recoveries and including interest charges

---

### Chunk 46: `b_47_atomic` (table)
- **Section**: `sample-tables.pdf > trends, 1980 to 2010. Source: Barro-Lee March, 2010`
- **Metadata**: `{'table_id': 'b_47', 'is_atomic': True, 'row_range': [0, 7], 'total_rows': 7, 'section_path': ['sample-tables.pdf', 'trends, 1980 to 2010. Source: Barro-Lee March, 2010'], 'preceding_prose_id': 'b_46', 'page_numbers': [8]}`

#### [A] Content for Vector Embedding (KV / Semantic Linearization):

```text
Section: sample-tables.pdf > trends, 1980 to 2010. Source: Barro-Lee March, 2010
Table Title: Table 21: footnotes replaced by additional table summary text
Row 1: Expenditure by function £million: Policy functions; Expenditure by function £million: Financial; 2009/10: 22.5; 2010/11: 30.57
Row 2: Expenditure by function £million: Policy functions; Expenditure by function £million: Information; 2009/10: 10.2; 2010/11: 14.8
Row 3: Expenditure by function £million: Policy functions; Expenditure by function £million: Contingency; 2009/10: 2.6; 2010/11: 1.2
Row 4: Expenditure by function £million: Remunerated functions; Expenditure by function £million: Agency services; 2009/10: 44.7; 2010/11: 35.91
Row 5: Expenditure by function £million: Remunerated functions; Expenditure by function £million:
... [truncated]
```

#### [B] Content for LLM Context Generation:

**Table 21: footnotes replaced by additional table summary text**

| Expenditure by function £million | Expenditure by function £million | 2009/10 | 2010/11 |
| --- | --- | --- | --- |
| Policy functions | Financial | 22.5 | 30.57 |
| Policy functions | Information | 10.2 | 14.8 |
| Policy functions | Contingency | 2.6 | 1.2 |
| Remunerated functions | Agency services | 44.7 | 35.91 |
| Remunerated functions | Payments | 22.41 | 19.88 |
| Remunerated functions | Banking | 22.90 | 44.23 |
| Remunerated functions | Other | 12.69 | 10.32 |

---

### Chunk 47: `b_48` (paragraph)
- **Section**: `sample-tables.pdf > trends, 1980 to 2010. Source: Barro-Lee March, 2010`
- **Metadata**: `{'section_path': ['sample-tables.pdf', 'trends, 1980 to 2010. Source: Barro-Lee March, 2010'], 'parent_id': 'b_40', 'level': 0, 'page': 1}`

#### [A] Content for Vector Embedding (KV / Semantic Linearization):

```text
[sample-tables.pdf > trends, 1980 to 2010. Source: Barro-Lee March, 2010]
Table 21: footnotes replaced by additional table summary text
```

#### [B] Content for LLM Context Generation:

> Table 21: footnotes replaced by additional table summary text

---

### Chunk 48: `b_49_atomic` (table)
- **Section**: `sample-tables.pdf > trends, 1980 to 2010. Source: Barro-Lee March, 2010`
- **Metadata**: `{'table_id': 'b_49', 'is_atomic': True, 'row_range': [0, 7], 'total_rows': 7, 'section_path': ['sample-tables.pdf', 'trends, 1980 to 2010. Source: Barro-Lee March, 2010'], 'preceding_prose_id': 'b_48', 'page_numbers': [8]}`

#### [A] Content for Vector Embedding (KV / Semantic Linearization):

```text
Section: sample-tables.pdf > trends, 1980 to 2010. Source: Barro-Lee March, 2010
Table Title: Table 22: referencing multiple endnotes from within a table
Row 1: Notes: on 1; 2010: 10.2; 2011: (Notes located page [n]) Information 14.8
Row 2: Expenditure £m: Contingency; 2010: 2.6; 2011: 1.2
Row 3: Expenditure £m: Payments; Notes: 3; 2010: 22.41; 2011: 19.88
Row 4: Expenditure £m: Banking; Notes: 4; 2010: 22.90; 2011: services 44.23
Row 5: Expenditure £m: Interest; 2010: 0.23; 2011: 0.10
Row 6: Expenditure £m: Dividends; Notes: 23; 2010: 2.5; 2011: 3.68
Row 7: Expenditure £m: Other; Notes: 9; 2010: 12.69; 2011: 10.32
```

#### [B] Content for LLM Context Generation:

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

---

### Chunk 49: `b_50` (paragraph)
- **Section**: `sample-tables.pdf > trends, 1980 to 2010. Source: Barro-Lee March, 2010`
- **Metadata**: `{'section_path': ['sample-tables.pdf', 'trends, 1980 to 2010. Source: Barro-Lee March, 2010'], 'parent_id': 'b_40', 'level': 0, 'page': 1}`

#### [A] Content for Vector Embedding (KV / Semantic Linearization):

```text
[sample-tables.pdf > trends, 1980 to 2010. Source: Barro-Lee March, 2010]
Table 22: referencing multiple endnotes from within a table
```

#### [B] Content for LLM Context Generation:

> Table 22: referencing multiple endnotes from within a table

---

### Chunk 50: `b_51_atomic` (table)
- **Section**: `sample-tables.pdf > trends, 1980 to 2010. Source: Barro-Lee March, 2010`
- **Metadata**: `{'table_id': 'b_51', 'is_atomic': True, 'row_range': [0, 2], 'total_rows': 2, 'section_path': ['sample-tables.pdf', 'trends, 1980 to 2010. Source: Barro-Lee March, 2010'], 'preceding_prose_id': 'b_50', 'page_numbers': [8]}`

#### [A] Content for Vector Embedding (KV / Semantic Linearization):

```text
Section: sample-tables.pdf > trends, 1980 to 2010. Source: Barro-Lee March, 2010
Table Title: Table 23: simulated table created using tabs and containing no structure
Row 1: Name: Bob; 2008.Entered: 22; 2008.Completed: 21; 2009.Entered: 20; 2009.Completed: 19
Row 2: Name: Sue; 2008.Entered: 44; 2008.Completed: 12; 2009.Entered: 12; 2009.Completed: 10
```

#### [B] Content for LLM Context Generation:

**Table 23: simulated table created using tabs and containing no structure**

| Name | 2008.Entered | 2008.Completed | 2009.Entered | 2009.Completed |
| --- | --- | --- | --- | --- |
| Bob | 22 | 21 | 20 | 19 |
| Sue | 44 | 12 | 12 | 10 |

---

### Chunk 51: `b_52` (paragraph)
- **Section**: `sample-tables.pdf > trends, 1980 to 2010. Source: Barro-Lee March, 2010`
- **Metadata**: `{'section_path': ['sample-tables.pdf', 'trends, 1980 to 2010. Source: Barro-Lee March, 2010'], 'parent_id': 'b_40', 'level': 0, 'page': 1}`

#### [A] Content for Vector Embedding (KV / Semantic Linearization):

```text
[sample-tables.pdf > trends, 1980 to 2010. Source: Barro-Lee March, 2010]
Table 23: simulated table created using tabs and containing no structure
```

#### [B] Content for LLM Context Generation:

> Table 23: simulated table created using tabs and containing no structure

---

### Chunk 52: `b_53_atomic` (table)
- **Section**: `sample-tables.pdf > trends, 1980 to 2010. Source: Barro-Lee March, 2010`
- **Metadata**: `{'table_id': 'b_53', 'is_atomic': True, 'row_range': [0, 12], 'total_rows': 12, 'section_path': ['sample-tables.pdf', 'trends, 1980 to 2010. Source: Barro-Lee March, 2010'], 'preceding_prose_id': 'b_52', 'page_numbers': [9]}`

#### [A] Content for Vector Embedding (KV / Semantic Linearization):

```text
Section: sample-tables.pdf > trends, 1980 to 2010. Source: Barro-Lee March, 2010
Table Title: Table 24: year-end financial statement (£, thousands)
Row 1: : Non-current assets
Row 2: : Buildings; 2010: 345; 2009: 445; 2008: 222
Row 3: : Investment; 2010: 567; 2009: 654; 2008: 423
Row 4: : Intangibles; 2010: 423; 2009: 123; 2008: 453
Row 5: : Current assets
Row 6: : Trade; 2010: 435; 2009: 634; 2008: 231
Row 7: : Cash; 2010: 524; 2009: 123; 2008: 482
Row 8: : Other; 2010: 223; 2009: 211; 2008: 254
Row 9: : Current liabilities
Row 10: : Trade liabilities; 2010: 154; 2009: 125; 2008: 421
Row 11: : Financial debt; 2010: 231; 2009: 474; 2008: 572
Row 12: : Provisions; 2010: 111; 2009: 312; 2008: 347
```

#### [B] Content for LLM Context Generation:

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

---

### Chunk 53: `b_54` (paragraph)
- **Section**: `sample-tables.pdf > trends, 1980 to 2010. Source: Barro-Lee March, 2010`
- **Metadata**: `{'section_path': ['sample-tables.pdf', 'trends, 1980 to 2010. Source: Barro-Lee March, 2010'], 'parent_id': 'b_40', 'level': 0, 'page': 1}`

#### [A] Content for Vector Embedding (KV / Semantic Linearization):

```text
[sample-tables.pdf > trends, 1980 to 2010. Source: Barro-Lee March, 2010]
Table 24: year-end financial statement (£, thousands)
```

#### [B] Content for LLM Context Generation:

> Table 24: year-end financial statement (£, thousands)

---

### Chunk 54: `b_55_atomic` (table)
- **Section**: `sample-tables.pdf > trends, 1980 to 2010. Source: Barro-Lee March, 2010`
- **Metadata**: `{'table_id': 'b_55', 'is_atomic': True, 'row_range': [0, 3], 'total_rows': 3, 'section_path': ['sample-tables.pdf', 'trends, 1980 to 2010. Source: Barro-Lee March, 2010'], 'preceding_prose_id': 'b_54', 'page_numbers': [9]}`

#### [A] Content for Vector Embedding (KV / Semantic Linearization):

```text
Section: sample-tables.pdf > trends, 1980 to 2010. Source: Barro-Lee March, 2010
Table Title: Table 25: setting column and row scope via the tags panel
Row 1: Name: Bob; 2008.Entered: 22; 2008.Won: 21; 2009.Entered: 20; 2009.Won: 19
Row 2: Name: Sue; 2008.Entered: 44; 2008.Won: 12; 2009.Entered: 12; 2009.Won: 10
Row 3: Name: Sam; 2008.Entered: 16; 2008.Won: 4; 2009.Entered: 45; 2009.Won: 30
```

#### [B] Content for LLM Context Generation:

**Table 25: setting column and row scope via the tags panel**

| Name | 2008.Entered | 2008.Won | 2009.Entered | 2009.Won |
| --- | --- | --- | --- | --- |
| Bob | 22 | 21 | 20 | 19 |
| Sue | 44 | 12 | 12 | 10 |
| Sam | 16 | 4 | 45 | 30 |

---

### Chunk 55: `b_56` (paragraph)
- **Section**: `sample-tables.pdf > trends, 1980 to 2010. Source: Barro-Lee March, 2010`
- **Metadata**: `{'section_path': ['sample-tables.pdf', 'trends, 1980 to 2010. Source: Barro-Lee March, 2010'], 'parent_id': 'b_40', 'level': 0, 'page': 1}`

#### [A] Content for Vector Embedding (KV / Semantic Linearization):

```text
[sample-tables.pdf > trends, 1980 to 2010. Source: Barro-Lee March, 2010]
Table 25: setting column and row scope via the tags panel
```

#### [B] Content for LLM Context Generation:

> Table 25: setting column and row scope via the tags panel

---

### Chunk 56: `b_57_atomic` (table)
- **Section**: `sample-tables.pdf > trends, 1980 to 2010. Source: Barro-Lee March, 2010`
- **Metadata**: `{'table_id': 'b_57', 'is_atomic': True, 'row_range': [0, 6], 'total_rows': 6, 'section_path': ['sample-tables.pdf', 'trends, 1980 to 2010. Source: Barro-Lee March, 2010'], 'preceding_prose_id': 'b_56', 'page_numbers': [9]}`

#### [A] Content for Vector Embedding (KV / Semantic Linearization):

```text
Section: sample-tables.pdf > trends, 1980 to 2010. Source: Barro-Lee March, 2010
Table Title: Table 26: courses offered by Institution X. A = Bachelor of Science, B = Bachelor of Arts, C = Masters, D = Doctorate, E = Diploma
Row 1: : Economics; 2006: A, B; 2007: A, C; 2008: A, C; 2009: A, C
Row 2: : International relations; 2006: A, E; 2007: A, E; 2008: A, B; 2009: A, B
Row 3: : Philosophy; 2006: A; 2007: A; 2008: A; 2009: A
Row 4: : Politics; 2006: A, D; 2007: A, D; 2008: A, B; 2009: A
Row 5: : Mathematics; 2006: B, C; 2007: B; 2008: A, B; 2009: A, B
Row 6: : English; 2006: A, C; 2007: A, B; 2008: A,B; 2009: A, C
```

#### [B] Content for LLM Context Generation:

**Table 26: courses offered by Institution X. A = Bachelor of Science, B = Bachelor of Arts, C = Masters, D = Doctorate, E = Diploma**

|  | 2006 | 2007 | 2008 | 2009 |
| --- | --- | --- | --- | --- |
| Economics | A, B | A, C | A, C | A, C |
| International relations | A, E | A, E | A, B | A, B |
| Philosophy | A | A | A | A |
| Politics | A, D | A, D | A, B | A |
| Mathematics | B, C | B | A, B | A, B |
| English | A, C | A, B | A,B | A, C |

---

### Chunk 57: `b_58` (paragraph)
- **Section**: `sample-tables.pdf > trends, 1980 to 2010. Source: Barro-Lee March, 2010`
- **Metadata**: `{'section_path': ['sample-tables.pdf', 'trends, 1980 to 2010. Source: Barro-Lee March, 2010'], 'parent_id': 'b_40', 'level': 0, 'page': 1}`

#### [A] Content for Vector Embedding (KV / Semantic Linearization):

```text
[sample-tables.pdf > trends, 1980 to 2010. Source: Barro-Lee March, 2010]
Table 26: courses offered by Institution X. A = Bachelor of Science, B = Bachelor of Arts, C = Masters, D = Doctorate, E = Diploma
```

#### [B] Content for LLM Context Generation:

> Table 26: courses offered by Institution X. A = Bachelor of Science, B = Bachelor of Arts, C = Masters, D = Doctorate, E = Diploma

---

### Chunk 58: `b_60_atomic` (table)
- **Section**: `sample-tables.pdf > Table 27: "table" with columns simulated by using tab stops`
- **Metadata**: `{'table_id': 'b_60', 'is_atomic': True, 'row_range': [0, 3], 'total_rows': 3, 'section_path': ['sample-tables.pdf', 'Table 27: "table" with columns simulated by using tab stops'], 'preceding_prose_id': None, 'page_numbers': [10]}`

#### [A] Content for Vector Embedding (KV / Semantic Linearization):

```text
Section: sample-tables.pdf > Table 27: "table" with columns simulated by using tab stops
Row 1: Name: 20; Apples: 25; Pears: Bob Scott
Row 2: Name: 24; Apples: 15; Pears: Susan. P. Arnold-Jones, BA, FRSA, MD
Row 3: Name: 14; Apples: 10; Pears: Sam Holder-Dickinson
```

#### [B] Content for LLM Context Generation:

| Name | Apples | Pears |
| --- | --- | --- |
| 20 | 25 | Bob Scott |
| 24 | 15 | Susan. P. Arnold-Jones, BA, FRSA, MD |
| 14 | 10 | Sam Holder-Dickinson |

---

### Chunk 59: `b_62_atomic` (table)
- **Section**: `sample-tables.pdf > Table 28: year-end financial table (£, thousands) - headings problem revisited`
- **Metadata**: `{'table_id': 'b_62', 'is_atomic': True, 'row_range': [0, 12], 'total_rows': 12, 'section_path': ['sample-tables.pdf', 'Table 28: year-end financial table (£, thousands) - headings problem revisited'], 'preceding_prose_id': None, 'page_numbers': [10]}`

#### [A] Content for Vector Embedding (KV / Semantic Linearization):

```text
Section: sample-tables.pdf > Table 28: year-end financial table (£, thousands) - headings problem revisited
Row 1: : Non-current assets
Row 2: : Buildings; 2010: 345; 2009: 445; 2008: 222
Row 3: : Investment; 2010: 567; 2009: 654; 2008: 423
Row 4: : Intangibles; 2010: 423; 2009: 123; 2008: 453
Row 5: : Current assets
Row 6: : Trade; 2010: 435; 2009: 634; 2008: 231
Row 7: : Cash; 2010: 524; 2009: 123; 2008: 482
Row 8: : Other; 2010: 223; 2009: 211; 2008: 254
Row 9: : Current liabilities
Row 10: : Trade liabilities; 2010: 154; 2009: 125; 2008: 421
Row 11: : Financial debt; 2010: 231; 2009: 474; 2008: 572
Row 12: : Provisions; 2010: 111; 2009: 312; 2008: 347
```

#### [B] Content for LLM Context Generation:

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

---

### Chunk 60: `b_63` (paragraph)
- **Section**: `sample-tables.pdf > Table 28: year-end financial table (£, thousands) - headings problem revisited`
- **Metadata**: `{'section_path': ['sample-tables.pdf', 'Table 28: year-end financial table (£, thousands) - headings problem revisited'], 'parent_id': 'b_61', 'level': 0, 'page': 1}`

#### [A] Content for Vector Embedding (KV / Semantic Linearization):

```text
[sample-tables.pdf > Table 28: year-end financial table (£, thousands) - headings problem revisited]
Table 29: multiple headers attributes for each data cell
```

#### [B] Content for LLM Context Generation:

> Table 29: multiple headers attributes for each data cell

---

### Chunk 61: `b_64_atomic` (table)
- **Section**: `sample-tables.pdf > Table 28: year-end financial table (£, thousands) - headings problem revisited`
- **Metadata**: `{'table_id': 'b_64', 'is_atomic': True, 'row_range': [0, 12], 'total_rows': 12, 'section_path': ['sample-tables.pdf', 'Table 28: year-end financial table (£, thousands) - headings problem revisited'], 'preceding_prose_id': 'b_63', 'page_numbers': [11]}`

#### [A] Content for Vector Embedding (KV / Semantic Linearization):

```text
Section: sample-tables.pdf > Table 28: year-end financial table (£, thousands) - headings problem revisited
Row 1: : 2010; South America: 2010; Asia: 2010; Africa: 2010; Australia: 2010
Row 2: : Highest average; South America: 523.6; Asia: 467.4; Africa: 405.0; Australia: 340.5
Row 3: : Highest in 24 hours; South America: 73.1; Asia: 54.1; Africa: 27.2; Australia: 66.3
Row 4: : Highest in 12 hours; South America: 42.4; Asia: 30.1; Africa: 15.9; Australia: 40.3
Row 5: : 2009; South America: 2009; Asia: 2009; Africa: 2009; Australia: 2009
Row 6: : Highest average; South America: 487.7; Asia: 453.6; Africa: 398.7; Australia: 356
Row 7: : Highest in 24 hours; South America: 67.2; Asia: 53.2; Africa: 44.3; Australia: 53.8
Row 8: : Highest in 12 hours; South America: 34.7; Asia: 34.1; Africa: 29
... [truncated]
```

#### [B] Content for LLM Context Generation:

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
| 2008 | 2008 | 2008 | 2008 | 2008 |
| Highest average | 496.7 | 444.3 | 502.1 | 399.6 |
| Highest in 24 hours | 44.2 | 56.7 | 32.1 | 63.2 |
| Highest in 12 hours | 30.1 | 32.7 | 21.9 | 40.2 |

---
