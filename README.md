
# Introduction
This is Python based program that combines multiple *.txt or *.rtf files into FDA specified format. The program also has a support for creating a table of contents with hyperlinks leading to chapters.  

The program is open source and free to use developed by [Aastat](https://aastat.com). The program is written and maintained  for the time being by @MesRoto so if you have question feel free to contact either one. 

## Running The Program
The program has been packaged into Creator.exe that contains all the relevant packages that the program needs to run except Microsoft Word or LibreOffice for converting rtf files into pdf files. In other words if you have either Microsoft Word or LibreOffice installed there is no need to download or install anything but the Creator.exe. 

When assembling PDF from the RTF files it is very important not to open backend converted (Microsoft Word or Libreoffice)

![Example picture 1](https://github.com/Aastat-FI/PDF_Converter/blob/master/ExamplePictures/example1.png?raw=true)
![Example picture 2](https://github.com/Aastat-FI/PDF_Converter/blob/master/ExamplePictures/example2.png?raw=true)

## How Does It Work?
### *txt files:
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

    "[\d]{4}[A-z0-9\\ /-:-().]*Program"

Meaning that the "Chapter" name is somewhere between 4 numbers and *"Program"*. Word "Program" can be changed from settings.  With this and information how long each generated PDF is we can compile table of contents with the pdf_template function which was used when making *.txt file conversion. 

If there is an error extracting "Chapter" name we set it to name of the file.

After this we can join the converted PDF files and table of content file together, append the hyperlinks to new PDF and finally save the generated PDF.

## TODO:
 - Open issue or contact aforementioned maintainers if you encounter any trouble
 - Fix issue needing to restart program
 - Load settings either from .csv or from .json
