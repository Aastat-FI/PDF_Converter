

# Introduction
This is Python based program that combines multiple *.txt or *.rtf files into FDA specified format. The program also has a support for creating a table of contents with hyperlinks leading to chapters.  

The program is open source and free to use developed by [Aastat](https://aastat.com). The program is written and maintained  for the time being by @MesRoto so if you have question feel free to contact either one. 

## Running The Program
The program has been packaged into Creator.exe that contains all the relevant packages that the program needs to run except Microsoft Word or LibreOffice for converting rtf files into pdf files. In other words you don't need to install python or any other libraries but the *.exe file needs to be in the same folder as the other *.py and settings file.

When assembling PDF from the RTF files it is very important not to open backend converted (Microsoft Word or Libreoffice)

![Example picture 1](https://github.com/Aastat-FI/PDF_Converter/blob/master/ExamplePictures/example1.png?raw=true)
![Example picture 2](https://github.com/Aastat-FI/PDF_Converter/blob/master/ExamplePictures/example2.png?raw=true)

## How Does It Work?
### *.txt files:
Text files are broken into blocks separated by long dashed lines. There are two kinds of text blocks: blocks that contain statistics from study and blocks that contain metadata such as name of the research or program info.

Program info, name of the "chapter", study name and sponsor are extracted from the metadata blocks. 
- Research name is defined name as the first row that contains text
- "Chapter" is defined as the second row of text
- Program info that appears in the footer is defined as the line that contains word "Program"

PDF is assembled to format specified by pdf_template class. Text blocks are broken into rows and inserted as fpdf cells to the document. Metadata extracted from the original files are inserted into footer or header.

### *.rtf files:
Functionality converting Rich Text Format files is done by create_pdf_from_rtf_files function in the main_functions folder. Rich Text Format files are converted to PDF files by the backend converted specified earlier.  

If the user wants to generated table of contents:
From the converted PDF only metadata we need is the chapter name for the table of contents. If user chooses to not to generate table of contents there is no need to worry about metadata. When the RTF is converted to PDF and then read as a string the string has header and footer together. With this information we can extract the chapter name with the regex:

    "START_WORD[A-z0-9\\ /-:-().]*END_WORD"

Meaning that the "Chapter" name is somewhere between START_WORD and END_WORD. Both of these words can be changed from settings. If the first word is not found then program uses only the end word parameter extracts all text. With this and information how long each generated PDF is we can compile table of contents with the pdf_template function which was used when making *.txt file conversion. 

If there is an error extracting "Chapter" name we set it to name of the file.

After this we can join the converted PDF files and table of content file together, append the hyperlinks to new PDF and finally save the generated PDF.

## Settings.csv
In this file you can change multiple settings related to parsing and output of the pdf document.

Some settings you need to check before converting your document:

 - "First word in footer": This needs to be the first unique word that you have after your tables.
	 - It is used in parsing the *.txt files when you don't have two linebreaks (see related setting) and trying to find title of the *.rtf file automatically
 - "Last word in header": This needs to be the first unique word that you have before your tables.
	 - Is needed when trying to find the title for the *.rtf files automatically
 - "Max header lines": Number of lines that the header may contain.
	 -  Used only in *.txt file conversion. If you don't have linebreak after your title you need to set this to relevant number. If there is a linebreak and you are having trouble set this to a large number
 - "Two linebreaks": Set to True when you have two linebreaks in each page. 
	 - Only used with *.txt files
 - "Line symbol": Symbol that tells the program what linebreak is used.
 - "TOC level": If there is text before your title set this to a number of rows that the text has (eg. sponsor or study information). If the document starts with title text set this to 0
	 - Only used with *.txt files

Graphical settings:

 - "Header y-offset": Millimeters from top of the page to header 
 - "Distance between header and chapter title": Millimeters from header to title of the page
 - "Chapter body x-offset": Millimeters from left side of the page to the text body
 - "Chapter body y-offset": Millimeters from top of the page to the text body
 - "Footer y-offset from bottom": Millimeters from the bottom of the page to footer. Must be negative
 -  "Distance between lower-dashed line and footer": Milllimeters from the lower linebreak to footer
 -   "TOC x-offset" Millimeters from the left side of the page to the table of contents text 
 - "Distance between lines of chapter body": Millimeters between lines in text body
 -   "Toc font size": Font size for table of contents. 
	 - You must adjust "Items on vertical/horizontal toc" and "Vertical/Horizontal Toc characters per line to reflect the changes. 
	 - Probably trial and error  
 - "PDF name": Name of the compiled pdf
 -  "Items on horizontal/vertical toc": Needed to adjust if you play with font size. 
 - "Vertical/Horizontal Toc characters per line": Same as above



## TODO:
 - Open issue or contact aforementioned maintainers if you encounter any trouble
 - Fix issue needing to restart program
 - Load settings either from .csv or from .json
