import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
import os
import pickle as pk
import gzip
import base64
from random import randint


### ----- GET INFO ----- ###

books = pk.load(open('book_ref2','rb'))
authors = pk.load(open('authors2','rb'))
authors_unique = authors.drop_duplicates('main_author')

## Cosine Similatity for books: ##
f = gzip.open('books_cosine2','rb')
ratings_matrix = pk.load(f)
f.close()
## Cosine similarity for authors: ##
ratings_matrix2 = pk.load(open("author_cosine","rb"))

## Comic strips ##
comic = 'comic.png'
encoded_comic = base64.b64encode(open(comic, 'rb').read())

## Function to create the header ##
def get_header():
    header = html.Div([

        html.Div([
            html.H5(
                'Bookworm: A Book Recommender')
        ], className="twelve columns padded", 
        style = {
          'background-color':'#2C5E51',
          'color':'#FEFEFE',
          'padding-left':'20',
          'padding-top': '20'
        })

    ])
    return header

## Function to create the menu ##
def get_menu():
  
    menu = html.Div([

        dcc.Link('By Book   ', href='/by-book', className="two columns"),

        dcc.Link('By Author   ', href='/by-author', className="two columns"),
        
        dcc.Link('Random   ', href='/random', className="two columns"),

    ], className="row ")
    return menu

## Function to save info on user selected book ##
def input_info(user_input,column):
  
  # Isolate index from user selection to ID the book in dataframe
  inp = books[books[column]==(user_input)].index.tolist()
  inp = inp[0]
  
  title = books['title'][int(str(inp).strip('[]'))]
  author = 'By: {}'.format(books['authors'][int(str(inp).strip('[]'))])
  date = 'Published: {}'.format(int(books['original_publication_year'][int(str(inp).strip('[]'))]))
  rating = 'Avg. GR rating: {}'.format(books['average_rating'][int(str(inp).strip('[]'))])
  link = 'https://www.goodreads.com/book/show/{}'.format(books['best_book_id'][int(str(inp).strip('[]'))])
  image = books['image_url'][int(str(inp).strip('[]'))]
  
  return title, author, date, rating, link, image
 
## Function to find similarity scores for user book input and save info for recommendation ##
def book_reco(user_input,options,options2,date_range,reco_number):
  
  # Isolate index from user selection to ID the book in dataframe
  inp = books[books['title']==(user_input)].index.tolist()
  inp=inp[0]
  
  # Match cosine similarities of books back into df
  reco = books
  reco['similarity'] = ratings_matrix.iloc[inp]
  reco = reco.sort_values(['similarity'], ascending = False)
  
  # Only show books published within time range from slider
  # Utilizes a dictionary to convert slider value to date
  t_dict = {0:-800,1:1800,2:1900,3:1950,4:1975,5:2000,6:2010,7:2018}
  t = [t_dict[date_range[0]],t_dict[date_range[1]]]
  reco = reco[reco.original_publication_year.between(t[0], t[1], inclusive=True)]
  
  # Check if book reco is in the same series based on user input
  if options2 == 'No':
  	reco = reco[(~reco['title'].str.contains('#')) & (~reco['title'].str.contains(','))]
  	
  # Check if reco is from same author, based on user input
  if options == 'No':
  	auth = books['authors'][inp]
  	auth = auth.split(',',2)[0]
  	reco = reco[reco['authors'].str.contains(auth)==False]
  	reco = reco[['title','authors','original_publication_year','average_rating','best_book_id','image_url','similarity']][0:5]
  else:
  	reco = reco[['title','authors','original_publication_year','average_rating','best_book_id','image_url','similarity']][0:5]
  	
  # Create container to show reco image and information
  choice = reco.iloc[[reco_number-1]]; 
  ind = choice.index.tolist(); 
  image = choice.image_url[int(str(ind).strip('[]'))]
  title = choice.title[int(str(ind).strip('[]'))]; 
  author = 'By: {}'.format(choice.authors[int(str(ind).strip('[]'))]); 
  date = 'Published: {}'.format(int(choice.original_publication_year[int(str(ind).strip('[]'))])); 
  rating = 'Avg. GR rating: {}'.format(choice.average_rating[int(str(ind).strip('[]'))]);
  link = 'https://www.goodreads.com/book/show/{}'.format(choice['best_book_id'][int(str(ind).strip('[]'))])
  
  return image, title, author, date, rating, link

## Function to save info on user author input ##
def auth_info(auth_input,column):
  
  select = books[books[column].str.contains(auth_input)].sort_values('average_rating',ascending=False).iloc[[0]]
  ind = select.index[0]
  title = select['title'][int(str(ind).strip('[]'))]
  date = 'Published: {}'.format(int(select['original_publication_year'][int(str(ind).strip('[]'))]))
  rating = 'Avg. GR rating: {}'.format(select['average_rating'][int(str(ind).strip('[]'))])
  link = 'https://www.goodreads.com/book/show/{}'.format(select['best_book_id'][int(str(ind).strip('[]'))])
  image = books['image_url'][int(str(ind).strip('[]'))]
  
  return title, date, rating, link, image

## Function to find similarity scores for user author input and save info for recommendation ##
def auth_reco(user_input,date_range,reco_number):
  
  # Isolate index for selection
  inp = authors[authors['authors'].str.contains(user_input)].index.tolist()
  inp = inp[0]
  
  # Match cosine similarities of section in whole data frame
  ans = authors
  ans['similarity'] = ratings_matrix2.iloc[inp]
  ans2 = ans.sort_values(['similarity'], ascending = False)
  
  # Set the date range using a dictionary for slider values
  t_dict = {0:-800,1:1800,2:1900,3:1950,4:1975,5:2000,6:2010,7:2018}
  t = [t_dict[date_range[0]],t_dict[date_range[1]]]
  ans2 = ans2[ans2.original_publication_year.between(t[0], t[1], inclusive=True)]
  
  # Remove repeats of same author recommendations
  if ans2['authors'].str.contains(user_input).any():
  	ans2 = ans2[(~ans2['authors'].str.contains(user_input))]
  	ans2 = ans2[['authors','original_publication_year','similarity']][0:5]
  	
  # Container for information on author name
  choice1 = ans2.iloc[[reco_number-1]]; 
  ind1 = choice1.index.tolist();
  author1 = '{}'.format(choice1.authors[int(str(ind1).strip('[]'))]); 
  
  auth_reco = html.Div([
  	  html.Div(children=[
  	  	  html.Div(author1,
  	  	  	style={'font-weight':'bold',
  	  	  	'font-size':'18'}),
  	  ], className="twelve columns"),
  ])
  
  # Container for remainder of info
  bk_list = books[books['authors'].str.contains(author1)].sort_values('average_rating',ascending=False)
  
  auth_bk1 = bk_list.iloc[[0]]
  ind1 = auth_bk1.index.tolist(); 
  image1 = auth_bk1['image_url'][int(str(ind1).strip('[]'))]
  title1 = auth_bk1.title[int(str(ind1).strip('[]'))]; 
  pub1 = 'Published: {}'.format(int(auth_bk1.original_publication_year[int(str(ind1).strip('[]'))])); 
  rating1 = 'Avg. GR rating: {}'.format(auth_bk1.average_rating[int(str(ind1).strip('[]'))]);
  link1 = 'https://www.goodreads.com/book/show/{}'.format(auth_bk1['best_book_id'][int(str(ind1).strip('[]'))]);
  
  reco1 = html.Div([
  	  html.Div(children=[
  	  	  html.Img(src=image1)
  	  ], className="four columns"),
  	  
  	  html.Div(children=[
  	  	  html.Div(title1,
  	  	  	style={'font-weight':'bold','font-size':'18'}),
  	  	  html.Div(pub1),
  	  	  html.Div(rating1),
  	  	  html.A("Goodreads page", href=link1, target="_blank")
  	  ], className="eight columns")
  ])
  
  # Check if there are more than one book for that author to display
  if len(bk_list) > 1:
  	auth_bk2 = bk_list.iloc[[1]]
  	ind2 = auth_bk2.index.tolist(); 
  	image2 = auth_bk2['image_url'][int(str(ind2).strip('[]'))]
  	title2 = auth_bk2.title[int(str(ind2).strip('[]'))]; 
  	pub2 = 'Published: {}'.format(int(auth_bk2.original_publication_year[int(str(ind2).strip('[]'))])); 
  	rating2 = 'Avg. GR rating: {}'.format(auth_bk2.average_rating[int(str(ind2).strip('[]'))]);
  	link2 = 'https://www.goodreads.com/book/show/{}'.format(auth_bk2['best_book_id'][int(str(ind2).strip('[]'))]);
  	
  	reco2 = html.Div([
  		html.Div(children=[
  			html.Img(src=image2)
  		], className="four columns"),
  		
  		html.Div(children=[
  			html.Div(title2,
  			  style={'font-weight':'bold','font-size':'18'}),
  			html.Div(pub2),
  			html.Div(rating2),
  			html.A("Goodreads page", href=link2, target="_blank")
  		], className="eight columns")
  	])
  else:
  	reco2 = html.Div(' ')
  
  return auth_reco, reco1, reco2
  	

### ----- APP SETUP ----- ###

## Initialize Dash object ##
app = dash.Dash(__name__)
server = app.server
app.title = 'Bookworm'

## Suppress warning for multipages ##
app.config['suppress_callback_exceptions'] = True

## Describe the layout, or the UI, of the app ##
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])
    
## ----- BOOK PAGE LAYOUT -----##

bybook = html.Div([

        html.Div([

            # Header
            get_header(),
            html.Div(),
            html.Br([]),
            # Description
            html.P('On the hunt for a new book, but not sure know where to \
              start looking? This tool can help narrow your search! Using a \
              collaborative filtering engine, this recommender will find books \
              with the highest similarity scores with the one you already \
              love, based off a database of almost 6 million reviews of 10,000 \
              of the most popular books in the world, from over 50,000 \
              Goodreads users. Happy reading!',
              style={'padding-top':'20'}), 
            html.Img(src='data:image/png;base64,{}'.format(encoded_comic.decode()),
              style={'margin-left': '250'}),
            # Menu
            html.H6('Select Recommender Type:',
              className="twelve columns", 
              style={
              	'background-color':'#48899A',
              	'padding':'10',
              'color':'white'}),
            get_menu(),
            html.Br([]),

            # Row 3 - User selection

            html.Div([

                html.Div([
                    html.H6('BY BOOK - Select (or enter) a book that you like:',
                            className="twelve columns",
                            style={'background-color':'#577BB9',
                              'padding':'10',
                            'color':'white'}),

                    html.Br([]),
                    
                    # Dropdown has values from master df of book titles
                    dcc.Dropdown(
                      id='book_input',
                      options=[{'label': s[0], 'value': s[0]}
                      			for s in zip(books.title)]),
                    
                    html.Br([]),
                    
                    # Display info on user selection
                    html.Div(children=[
                    	html.Div(id='choice')
                    ], className="two columns"),
                    
                    html.Div(children=[
                    	html.Div(id='choice2')
                    ], className="nine columns",
                    style = {
                      'padding': '20px',
                    'fontSize' : 17})

                ], className="six columns"),
                
                # Column for user options selection
                html.Div([
                    html.H6(["Options"],
                            className="twelve columns",
                            style={'background-color':'#577BB9',
                              'padding':'10',
                            'color':'white'}),
                    
                    html.Br([]),
                    
                    # Option to check if reco from same author
                    html.H6(['Include books from the same author?']),
                    dcc.RadioItems(
                      options=[
                      	{'label': ' - Yes - ', 'value': 'Yes'},
                      	{'label': ' - No - ', 'value': 'No'}
                      ],
                      value='Yes',
                      id='same_author_choice',
                      labelStyle={'display': 'inline-block'}
                      ),
                    
                    # Option to check for same series
                    html.H6(['Include books from the same series (if applicable)?']),
                    dcc.RadioItems(
                      options=[
                      	{'label': ' - Yes - ', 'value': 'Yes'},
                      	{'label': ' - No - ', 'value': 'No'}
                      ],
                      value='Yes',
                      id='same_series_choice',
                      labelStyle={'display': 'inline-block'}
                      ),
                    
                    # Date range slider
                    html.H6(['From what range of dates?']),
                    dcc.RangeSlider(
                      id='date_range',
                      min=0,
                      max=7,
                      step=None,
                      marks={
                      	0: 'Ancient',
                      	1: '1800',
                      	2: '1900',
                      	3: '1950',
                      	4: '1975',
                      	5: '2000',
                      	6: '2010',
                        7: 'Present'},
                      value=[0, 7]
                      ),
                    
                    html.Br([]),
                    html.Br([]),
                    
                ], className="six columns"),

            ], className="row "),
            
            # Row 4 - Recommendations section
            
            html.Div([

                html.Div(children=[
                    html.H6('Your recommendations:',
                            className="twelve columns",
                            style={'background-color':'#AB6515',
                              'padding':'10',
                            'color':'white'}),

                    html.Br([]),
                    
                    # Row 1 of recommendations (two columns)
                    html.Div([
                    	html.Div(children=[
                    		html.Div(id='reco1')
                    	], className="six columns"),
                    
                    	html.Div(children=[
                    		html.Div(id='reco2')
                    	], className="six columns"),
                    	
                    ], className="twelve columns"),
                    
                    html.Br([]),
                    
                    # Row 2 of recommendations (two columns)
					html.Div([
                    	html.Div(children=[
                    		html.Div(id='reco3')
                    	], className="six columns"),
                    
                    	html.Div(children=[
                    		html.Div(id='reco4')
                    	], className="six columns"),
                    	
                    ], className="twelve columns"),
                    
                    html.Br([]),
                    
                    # Row 3 of recommendations (one column)
                    html.Div([
                    	html.Div(children=[
                    		html.Div(id='reco5')
                    	], className='six columns')
                    ])

                ], className="twelve columns")

            ], className="row "),
            
            ## Footer ##
            html.Div(children=[
            	html.Hr(),
            	html.H6(children='David Alfego',
            	  style={'font-style': 'italic'}),
            	dcc.Link('About', href='/about'),
            html.H1(' ')],
            className='twelve columns',
            style={'text-align': 'center', 'padding': '50'}),
        
        ], className="subpage")

    ], className="page",
    
    style={
        'width': '85%',
        'max-width': '1200',
        'margin-left': 'auto',
        'margin-right': 'auto',
        'fontSize': '16',
        'padding': '40',
        'padding-top': '20',
    	'padding-bottom': '50'},

)

## ----- BOOK PAGE CALLBACKS ----- ##

@app.callback(
  Output('choice', 'children'),
  [Input('book_input', 'value')]
  )
def book_choice_image(book_input):
  
  # Function to show image user selection
  
  # Isolate index that corresponds with selection in the data frame

  title, author, date, rating, link, image = input_info(book_input,'title')
  
  return html.Img(src=image)

#####

@app.callback(
  Output('choice2', 'children'),
  [Input('book_input', 'value')]
  )
def book_choice_text(book_input):
  
  title, author, date, rating, link, image = input_info(book_input,'title')
  
  # Container to display info
  children = html.Div([
  	  html.Div(title,
  	  	style={'font-weight':'bold',
  	  	'font-size':'18'}),
  	  html.Div(author),
  	  html.Div(date),
  	  html.Div(rating),
  	  html.A("Goodreads page", href=link, target="_blank")
  ])
  
  return children

#####

@app.callback(
  Output('reco1', 'children'),
  [Input('book_input', 'value'),
  Input('same_author_choice', 'value'),
  Input('same_series_choice', 'value'),
  Input('date_range', 'value')]
  )
def recommend1(book_input,options,options2,date_range):
  
  image, title, author, date, rating, link = book_reco(book_input,options,options2,date_range,1)
  
  reco1 = html.Div([
  	  html.Div(children=[
  	  	  html.Img(src=image)
  	  ], className="three columns"),
  	  
  	  html.Div(children=[
  	  	  html.Div(title,
  	  	  	style={'font-weight':'bold','font-size':'18'}),
  	  	  html.Div(author),
  	  	  html.Div(date),
  	  	  html.Div(rating),
  	  	  html.A("Goodreads page", href=link, target="_blank")
  	  ], className="eight columns")
  ])
  
  return reco1

#####

@app.callback(
  Output('reco2', 'children'),
  [Input('book_input', 'value'),
  Input('same_author_choice', 'value'),
  Input('same_series_choice', 'value'),
  Input('date_range', 'value')]
  )
def recommend2(book_input,options,options2,date_range):
  
  image, title, author, date, rating, link = book_reco(book_input,options,options2,date_range,2)
  
  reco2 = html.Div([
  	  html.Div(children=[
  	  	  html.Img(src=image)
  	  ], className="three columns"),
  	  
  	  html.Div(children=[
  	  	  html.Div(title,
  	  	  	style={'font-weight':'bold','font-size':'18'}),
  	  	  html.Div(author),
  	  	  html.Div(date),
  	  	  html.Div(rating),
  	  	  html.A("Goodreads page", href=link, target="_blank")
  	  ], className="eight columns")
  ])
  
  return reco2

#####

@app.callback(
  Output('reco3', 'children'),
  [Input('book_input', 'value'),
  Input('same_author_choice', 'value'),
  Input('same_series_choice', 'value'),
  Input('date_range', 'value')]
  )
def recommend3(book_input,options,options2,date_range):
  
  image, title, author, date, rating, link = book_reco(book_input,options,options2,date_range,3)
  
  reco3 = html.Div([
  	  html.Div(children=[
  	  	  html.Img(src=image)
  	  ], className="three columns"),
  	  
  	  html.Div(children=[
  	  	  html.Div(title,
  	  	  	style={'font-weight':'bold','font-size':'18'}),
  	  	  html.Div(author),
  	  	  html.Div(date),
  	  	  html.Div(rating),
  	  	  html.A("Goodreads page", href=link, target="_blank")
  	  ], className="eight columns")
  ])
  
  return reco3

#####

@app.callback(
  Output('reco4', 'children'),
  [Input('book_input', 'value'),
  Input('same_author_choice', 'value'),
  Input('same_series_choice', 'value'),
  Input('date_range', 'value')]
  )
def recommend4(book_input,options,options2,date_range):
  
  image, title, author, date, rating, link = book_reco(book_input,options,options2,date_range,4)
  
  reco4 = html.Div([
  	  html.Div(children=[
  	  	  html.Img(src=image)
  	  ], className="three columns"),
  	  
  	  html.Div(children=[
  	  	  html.Div(title,
  	  	  	style={'font-weight':'bold','font-size':'18'}),
  	  	  html.Div(author),
  	  	  html.Div(date),
  	  	  html.Div(rating),
  	  	  html.A("Goodreads page", href=link, target="_blank")
  	  ], className="eight columns")
  ])
  
  return reco4

#####

@app.callback(
  Output('reco5', 'children'),
  [Input('book_input', 'value'),
  Input('same_author_choice', 'value'),
  Input('same_series_choice', 'value'),
  Input('date_range', 'value')]
  )
def recommend5(book_input,options,options2,date_range):
  
  image, title, author, date, rating, link = book_reco(book_input,options,options2,date_range,5)
  
  reco5 = html.Div([
  	  html.Div(children=[
  	  	  html.Img(src=image)
  	  ], className="three columns"),
  	  
  	  html.Div(children=[
  	  	  html.Div(title,
  	  	  	style={'font-weight':'bold','font-size':'18'}),
  	  	  html.Div(author),
  	  	  html.Div(date),
  	  	  html.Div(rating),
  	  	  html.A("Goodreads page", href=link, target="_blank")
  	  ], className="eight columns")
  ])
  
  return reco5


## ----- AUTHOR PAGE LAYOUT -----##

byauthor = html.Div([

        html.Div([

            # Header
            get_header(),
            html.Br([]),
            # Description
            html.P('On the hunt for a new book, but not sure know where to \
              start looking? This tool can help narrow your search! Using a \
              collaborative filtering engine, this recommender will find books \
              with the highest similarity scores with the one you already \
              love, based off a database of almost 6 million reviews of 10,000 \
              of the most popular books in the world, from over 50,000 \
              Goodreads users. Happy reading!',
              style={'padding-top':'20'}), 
            html.Img(src='data:image/png;base64,{}'.format(encoded_comic.decode()),
              style={'margin-left': '250'}),
            # Menu
            html.H6('Select Recommender Type:',
              className="twelve columns", 
              style={
              	'background-color':'#48899A',
              	'padding':'10',
              'color':'white'}),
            get_menu(),
            html.Br([]),

            # Row 3 - User input

            html.Div([

                html.Div([
                    html.H6('BY AUTHOR - Select (or enter) an author that you like:',
                            className="twelve columns",
                            style={'background-color':'#630b0b',
                              'padding':'10',
                            'color':'white'}),

                    html.Br([]),
                    
                    # Dropdown menu to select an author utilizes author list from pickle
                    
                    dcc.Dropdown(
                      id='auth_input',
                      options=[{'label': m[0], 'value': m[0]}
                      			for m in zip(authors_unique.main_author)]),
                    
                    html.Br([]),
                    
                    # Display the user choice, and author's best book
                    
                    html.Div(id='auth_choice1'),
                    
                    html.Div(children=[
                    	html.Div(id='auth_choice2')
                    ], className="two columns"),
                    
                    html.Div(children=[
                    	html.Div(id='auth_choice3')
                    ], className="nine columns",
                    style = {
                      'padding': '20px',
                    'fontSize' : 17}),
                    
                    html.Br([]),

                ], className="six columns"),

				# Options column for user choice
				
                html.Div([
                    html.H6(["Options"],
                            className="twelve columns",
                            style={'background-color':'#630b0b',
                              'padding':'10',
                            'color':'white'}),
                    
                    html.Br([]),
                    
                    # Slider for date ranges
                    html.H6(['From what range of dates?']),
                    dcc.RangeSlider(
                      id='date_range2',
                      min=0,
                      max=7,
                      step=None,
                      marks={
                      	0: 'Ancient',
                      	1: '1800',
                      	2: '1900',
                      	3: '1950',
                      	4: '1975',
                      	5: '2000',
                      	6: '2010',
                        7: 'Present'},
                      value=[0, 7]
                      ),
                    
                    html.Br([]),
                    html.Br([]),
                    
                ], className="six columns"),

            ], className="row "),
            
            # Row 4 - Recommendations
            
            html.Div([

                html.Div(children=[
                    html.H6('Your recommendations (and some books you may enjoy):',
                            className="twelve columns",
                            style={'background-color':'#AB6515',
                              'padding':'10',
                            'color':'white'}),

                    html.Br([]),
                    
                    # Display all the author recommendations: four rows, three columns
                    
                    html.Div(id='auth_reco1', 
                      className="twelve columns"),
                    
                    html.Div(id='auth_reco2', 
                      className="twelve columns"),
                    
                    html.Div(id='auth_reco3', 
                      className="twelve columns"),
                    
                    html.Div(id='auth_reco4', 
                      className="twelve columns"),
                    
                    html.Br([]),

                ], className="twelve columns")

            ], className="row "),
            
            ## Footer ##
            html.Div(children=[
            	html.Hr(),
            	html.H6(children='David Alfego',
            	  style={'font-style': 'italic'}),
            	dcc.Link('About', href='/about'),
            html.H1(' ')],
            className='twelve columns',
            style={'text-align': 'center', 'padding': '50'}),
        
        ], className="subpage")

    ], className="page",
    
    style={
        'width': '85%',
        'max-width': '1200',
        'margin-left': 'auto',
        'margin-right': 'auto',
        'fontSize': '16',
        'padding': '40',
        'padding-top': '20',
    	'padding-bottom': '50'},

)


## ----- AUTHOR PAGE CALLBACKS -----##

@app.callback(
  Output('auth_choice1', 'children'),
  [Input('auth_input', 'value')]
  )
def auth_choice(auth_input):
  
  # Function to show selected author's name
  
  a = html.Div([
  	  html.Div('{}'.format(auth_input),
  	  	style={'font-weight':'bold',
  	  	'font-size':'18'}),
  	  html.Div('The highest rated book from this author:')
  ])
  
  return a

#####

@app.callback(
  Output('auth_choice2', 'children'),
  [Input('auth_input', 'value')]
  )
def auth_choice_image(auth_input):
  
  # Function to show image of selected author's best book
  
  title, date, rating, link, image = auth_info(auth_input,'authors')
  
  return html.Img(src=image)

#####

@app.callback(
  Output('auth_choice3', 'children'),
  [Input('auth_input', 'value')]
  )
def auth_choice_text(auth_input):
  
  # Function to show info on selected author's best book
  
  title, date, rating, link, image = auth_info(auth_input,'authors')
  
  children = html.Div([
  	  html.Div(title,
  	  	style={'font-weight':'bold',
  	  	'font-size':'18'}),
  	  html.Div(date),
  	  html.Div(rating),
  	  html.A("Goodreads page", href=link, target="_blank")
  ])
  
  return children

#####

@app.callback(
  Output('auth_reco1', 'children'),
  [Input('auth_input', 'value'),
  Input('date_range2', 'value')]
  )
def auth_recommend1(auth_input,date_range):
  
  a_reco, reco1, reco2 = auth_reco(auth_input,date_range,1)
  
  full_author = html.Div(children=[
  	  html.Div(a_reco,
  	  	className="four columns"),
  	  
  	  html.Div(reco1,
  	  	className="four columns"),
  	  
  	  html.Div(reco2,
  	  	className="four columns"),
  ])
  
  return full_author

#####

@app.callback(
  Output('auth_reco2', 'children'),
  [Input('auth_input', 'value'),
  Input('date_range2', 'value')]
  )
def auth_recommend2(auth_input,date_range):
  
  a_reco, reco1, reco2 = auth_reco(auth_input,date_range,2)
  
  full_author = html.Div(children=[
  	  html.Div(a_reco,
  	  	className="four columns"),
  	  
  	  html.Div(reco1,
  	  	className="four columns"),
  	  
  	  html.Div(reco2,
  	  	className="four columns"),
  ])
  
  return full_author

#####

@app.callback(
  Output('auth_reco3', 'children'),
  [Input('auth_input', 'value'),
  Input('date_range2', 'value')]
  )
def auth_recommend3(auth_input,date_range):
  
  a_reco, reco1, reco2 = auth_reco(auth_input,date_range,3)
  
  full_author = html.Div(children=[
  	  html.Div(a_reco,
  	  	className="four columns"),
  	  
  	  html.Div(reco1,
  	  	className="four columns"),
  	  
  	  html.Div(reco2,
  	  	className="four columns"),
  ])
  
  return full_author

#####

@app.callback(
  Output('auth_reco4', 'children'),
  [Input('auth_input', 'value'),
  Input('date_range2', 'value')]
  )
def auth_recommend4(auth_input,date_range):
  
  a_reco, reco1, reco2 = auth_reco(auth_input,date_range,4)
  
  full_author = html.Div(children=[
  	  html.Div(a_reco,
  	  	className="four columns"),
  	  
  	  html.Div(reco1,
  	  	className="four columns"),
  	  
  	  html.Div(reco2,
  	  	className="four columns"),
  ])
  
  return full_author


## ----- RANDOM PAGE LAYOUT -----##

random = html.Div([

        html.Div([

            # Header
            get_header(),
            html.Br([]),
            ## Description ##
            html.P('On the hunt for a new book, but not sure know where to \
              start looking? This tool can help narrow your search! Using a \
              collaborative filtering engine, this recommender will find books \
              with the highest similarity scores with the one you already \
              love, based off a database of almost 6 million reviews of 10,000 \
              of the most popular books in the world, from over 50,000 \
              Goodreads users. Happy reading!',
              style={'padding-top':'20'}), 
            html.Img(src='data:image/png;base64,{}'.format(encoded_comic.decode()),
              style={'margin-left': '250'}),
            ## Menu ##
            html.H6('Select Recommender Type:',
              className="twelve columns", 
              style={
              	'background-color':'#48899A',
              	'padding':'10',
              'color':'white'}),
            get_menu(),
            html.Br([]),

            # Row 3 - Recommendation

            html.Div([

                html.Div(children=[
                    html.H6('Click the button for your random recommendation:',
                            className="twelve columns",
                            style={'background-color':'#AB6515',
                              'padding':'10',
                            'color':'white'}),
                    
                    html.Button('Find a book!', id='button',
                      style={
                    	'padding': '10',
                    	'padding-top': '5',
                    	'padding-bottom': '20',
                    	'align': 'center',
                      'fontSize': 14}),

                    html.Br([]),
                    
                    html.Div([
                    	html.Div(children=[
                    		html.Div(id='random_reco')
                    	], className="six columns"),
                    	
                    ], className="twelve columns"),
                    
                    html.Br([]),

                ], className="twelve columns")

            ], className="row "),
            
            ## Footer ##
            html.Div(children=[
            	html.Hr(),
            	html.H6(children='David Alfego',
            	  style={'font-style': 'italic'}),
            	dcc.Link('About', href='/about'),
            html.H1(' ')],
            className='twelve columns',
            style={'text-align': 'center', 'padding': '50'}),
        
        ], className="subpage")

    ], className="page",
    
    style={
        'width': '85%',
        'max-width': '1200',
        'margin-left': 'auto',
        'margin-right': 'auto',
        'fontSize': '16',
        'padding': '40',
        'padding-top': '20',
    	'padding-bottom': '50'},

)


## ----- RANDOM PAGE CALLBACKS -----##

@app.callback(
    dash.dependencies.Output('random_reco','children'),
    [dash.dependencies.Input('button','n_clicks')]) 
def update_output(n_clicks):
  
  # Button press will yield a result
  threshold =0
  if(n_clicks>threshold):
  	threshold=threshold+1
  
  # Random integer corresponding with an index for the books dataframe
  inp = randint(0,10000)
  
  # Container to display image and info
  image = books['image_url'][int(str(inp).strip('[]'))]
  title = books['title'][int(str(inp).strip('[]'))]
  author = 'By: {}'.format(books['authors'][int(str(inp).strip('[]'))])
  date = 'Published: {}'.format(int(books['original_publication_year'][int(str(inp).strip('[]'))]))
  rating = 'Avg. GR rating: {}'.format(books['average_rating'][int(str(inp).strip('[]'))])
  link = 'https://www.goodreads.com/book/show/{}'.format(books['best_book_id'][int(str(inp).strip('[]'))]);
  	
  rando = html.Div([
  	  html.Div(children=[
  	  	  html.Img(src=image)
  	  ], className="three columns"),
  	  
  	  html.Div(children=[
  	  	  html.Div(title,
  	  	  	style={'font-weight':'bold',
  	  	  	'font-size':'18'}),
  	  	  html.Div(author),
  	  	  html.Div(date),
  	  	  html.Div(rating),
  	  	  html.A("Goodreads page", href=link, target="_blank")
  	  ], className="eight columns")
  ])

  return rando


## ----- ABOUT PAGE LAYOUT -----##

about = html.Div([

        html.Div([

            ## Header ##
            get_header(),
            html.Br([]),
            ## Description ##
            html.P('On the hunt for a new book, but not sure know where to \
              start looking? This tool can help narrow your search! Using a \
              collaborative filtering engine, this recommender will find books \
              with the highest similarity scores with the one you already \
              love, based off a database of almost 6 million reviews of 10,000 \
              of the most popular books in the world, from over 50,000 \
              Goodreads users. Happy reading!',
              style={'padding-top':'20'}),
            html.P('This dashboard was created by David Alfego, utilizing \
              Dash by Plotly and hosted on Heroku. The dataset, \
              goodreads-10k, was obtained from FastML \
              (http://fastml.com/goodbooks-10k). The collaborative filtering \
              model uses cosine similarity to measure highest relationship \
              among categories. Thanks!',
              style={'padding-top':'20'}), 
            html.Br([]),
            ## Menu ##
            html.H6('Select Recommender Type:',
              className="twelve columns", 
              style={
              	'background-color':'#48899A',
              	'padding':'10',
              'color':'white'}),
            get_menu(),
            html.Br([]),
            
            ## Footer ##
            html.Div(children=[
            	html.Hr(),
            	html.H6(children='David Alfego',
            	  style={'font-style': 'italic'}),
            	dcc.Link('About', href='/about'),
            html.H1(' ')],
            className='twelve columns',
            style={'text-align': 'center', 'padding': '50'}),
        
        ], className="subpage")

    ], className="page",
    
    style={
        'width': '85%',
        'max-width': '1200',
        'margin-left': 'auto',
        'margin-right': 'auto',
        'fontSize': '16',
        'padding': '40',
        'padding-top': '20',
    	'padding-bottom': '50'},

)


## ----- NO PAGE LAYOUT -----##

noPage = html.Div([  # 404

    html.P(["404 Page not found"])

    ], className="no-page")


## ----- PAGE UPDATES/TABS -----##

@app.callback(
  dash.dependencies.Output('page-content', 'children'),
  [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
  if pathname == '/' or pathname == '/by-book':
  	return bybook
  elif pathname == '/by-author':
  	return byauthor
  elif pathname == '/random':
  	return random
  elif pathname == '/about':
  	return about
  else:
  	return noPage
  

### ----- TEMPLATE ----- ###

external_css = ["https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css",
                "https://cdn.rawgit.com/plotly/dash-app-stylesheets/737dc4ab11f7a1a8d6b5645d26f69133d97062ae/dash-wind-streaming.css",
                "https://fonts.googleapis.com/css?family=Raleway:400,400i,700,700i",
                "https://fonts.googleapis.com/css?family=Product+Sans:400,400i,700,700i"]


for css in external_css:
    app.css.append_css({"external_url": css})

if 'DYNO' in os.environ:
    app.scripts.append_script({
        'external_url': 'https://cdn.rawgit.com/chriddyp/ca0d8f02a1659981a0ea7f013a378bbd/raw/e79f3f789517deec58f41251f7dbb6bee72c44ab/plotly_ga.js'
    })


### ----- MAIN ----- ###

if __name__ == '__main__':

    app.run_server(debug=True)