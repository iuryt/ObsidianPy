import os
import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode


'''
This code parses bibitems from a .bib file and generates a markdown file for each bibitem. 
The markdown file contains all keys and values from the bibitem.
The markdown file is named after the citation key.
'''

# Path to your .bib file
bibfile = 'library.bib'

# Path to the folder where the markdown files will be generated
output_folder = '../../vault/Work/01-Literature/'

encoding = 'utf-8'

# function to create the template for the notes after the yaml frontmatter
def create_template(entry):
    template = "# `= this.title`\n"
    template = template + "`= this.author`\n"
    template = template + "*`= this.journal`*\n\n"
    template = template + "`= this.abstract`\n\n"
    template = template + "<!-- --- -->\n\n"
    return template

# Read the .bib file
with open(bibfile, encoding=encoding) as bibtex_file:
    parser = BibTexParser()
    parser.customization = convert_to_unicode
    bib_database = bibtexparser.load(bibtex_file, parser=parser)
    # convert the bibitems into a dictionary
    bib_database = bib_database.entries_dict


# Generate a markdown file for each bibitem
for key in bib_database:
    entry = bib_database[key]
    filename = entry['ID'] + '.md'

    # prepare the bibitem
    # remove the keys 'file' and 'keywords' from the bibitem if they are present
    if 'file' in entry:
        del entry['file']
    if 'keywords' in entry:
        del entry['keywords']
    # separate author by ' and '
    if 'author' in entry:
        entry['author'] = entry['author'].split(' and ')

    # if the bibitem contains an 'abstract' key
    if 'abstract' in entry:
        # select the abstract
        abstract = entry['abstract']
        # remove any 'abstract' words from the abstract
        abstract = abstract.replace('Abstract', '').replace('abstract', '')
        # remove any newlines from the abstract
        abstract = abstract.replace('\n', '')
        # remove any double spaces from the abstract
        abstract = " ".join(abstract.split())
        # replace the abstract in the bibitem with the cleaned abstract
        entry['abstract'] = "|\n    \"" + abstract + "\""

    else:
        entry['abstract'] = ""

    # if the bibitem contains a 'title' key, put it in quotation marks
    if 'title' in entry:
        entry['title'] = '"'+entry['title']+'"'

    # if the bibitem contains a 'journal' key, put it in quotation marks
    if 'journal' in entry:
        entry['journal'] = '"'+entry['journal']+'"'

    # if the file does not exist, create it
    if not os.path.exists(os.path.join(output_folder, filename)):

        # Write the markdown file
        with open(os.path.join(output_folder, filename), 'w', encoding=encoding) as f:
            # write the yaml frontmatter
            f.write('---\r')
            # write the bibitem keys and values
            for key, value in entry.items():
                f.write(f'{key}: {value}\r')
            # write the closing yaml frontmatter
            f.write('---\r\n\n')
            # write the template for the notes
            f.write(create_template(entry))
    
    # if the file already exists
    else:
        # read the whole file
        with open(os.path.join(output_folder, filename), 'r', encoding=encoding) as f:
            content = f.read()

        # if the yaml frontmatter is missing, add it
        if not content.startswith('---'):
            with open(os.path.join(output_folder, filename), 'w', encoding=encoding) as f:
                # write the yaml frontmatter
                f.write('---\r')
                # write the bibitem keys and values
                for key, value in entry.items():
                    f.write(f'{key}: {value}\r')
                # write the closing yaml frontmatter
                f.write('---\r')
        #if the yaml frontmatter is present, add the missing bibitem keys and values and update the existing ones
        else:
            # split the file into the header and the rest of the file
            header, notes = content.split('<!-- --- -->')
            # select the yaml frontmatter from the header
            frontmatter = header.split('---',2)[1]
            # remove the newline after | in the abstract
            frontmatter = frontmatter.replace('|\n', '|')
            # split the bibitem keys and values into a list of lines
            frontmatter = frontmatter.splitlines()
            # remove any empty lines
            frontmatter = [line for line in frontmatter if line]
            # convert the list of lines into a dictionary
            frontmatter = dict([line.split(': ', 1) for line in frontmatter])
            # add the newline after | in the abstract
            if 'abstract' in frontmatter:
                frontmatter['abstract'] = frontmatter['abstract'].replace('|', '|\n')

            # add the missing bibitem keys and values and update the existing ones
            for key, value in entry.items():
                frontmatter[key] = value
            # convert the dictionary into a list of lines
            frontmatter = [f'{key}: {value}' for key, value in frontmatter.items()]
            # sort the list of lines
            frontmatter.sort()
            # write the markdown file with the updated bibitem keys and values
            with open(os.path.join(output_folder, filename), 'w', encoding=encoding) as f:
                # write the yaml frontmatter
                f.write('---\r')
                # write the bibitem keys and values
                for line in frontmatter:
                    f.write(f'{line}\r')
                # write the closing yaml frontmatter
                f.write('---\r')
                # write the template for the notes
                f.write(create_template(entry))
                # write the rest of the file
                f.write(notes)