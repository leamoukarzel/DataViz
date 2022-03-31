import pandas as pd
import altair as alt
from altair import expr, datum
import datetime as dt
import streamlit as st

st.write('# Fake News on the Internet - BuzzFeed News Dataset')

st.write("In recent years, we have seen the emergence and multiplication of false information relayed on social networks and various websites. This phenomenon is commonly known as 'fake news'. ")
st.write("Over the past four years, BuzzFeed News has maintained lists of sites that publish completely fabricated stories. As they encounter new ones and debunk their content, they add them to the list. To produce this story, they used this list as well as some sites brought to their attention by fact-checking websites. ")
st.write("Thanks to this dataset, we wanted to study different aspects of this sociological phenomenon, whether it be their origin, their chronology or their typology. In a way, thanks to our project, we are trying to draw up a draft identity card of fake news. For our study, we focus on data available for 2018.")
# @st.cache decorator skip reloading the code when the app
@st.cache
def loadData():
    return pd.read_csv('top-2018-cleaned1.csv')

df = loadData()

st.write('## General overview of Fake News in 2018.')
st.write('In the two graphs below we look at the activity of fake news published throughout 2018.')
st.write('On the left graph, that represents the number of publications per day, we can see that the number of publications per day is relatively stable with a general growth over the whole year. Over the course of 2018, no major phenomenon has significantly changed the pace of the fake news phenomenon, except for a peak on July 20, where the number of fake news published has exploded. Scrolling to other graphs will help understand where this peak is coming from.')
st.write('The right graph represents the number of Facebook engagements per day and per domain name. As we can clearly see, the fake news published by a .com domain are the ones that generates the most engagement on Facebook.')

#@st.cache(allow_output_mutation=True)

# Pre-process dataframe
@st.cache
def pre_process(df):
	df = df[df['published_date'].str.contains("2018")].reset_index(drop=True)
	df['published_date'] = pd.to_datetime(df['published_date'])
	df['month'] = df['published_date'].dt.to_period('M').astype(str)
	df['month'] = pd.to_datetime(df['month'])
	df['month_int'] = [df['month'][x].month for x in range(len(df['month']))]
	df['year_int'] = [df['month'][x].year for x in range(len(df['month']))]
	df['category'] = df['category'].fillna('Not Available')

	return df

df = pre_process(df)
alt.data_transformers.disable_max_rows()
brush = alt.selection_interval(encodings=['x'])
# Define first graph - Daily publications
@st.cache(allow_output_mutation=True)
def graph1(df):
	fake_news_daily = alt.Chart(df, title = 'Number of publications per day').mark_line().encode(
    	x='published_date:T',
    	y=alt.Y('count(titre):Q'),
    	tooltip=['published_date:T', 'count(titre):Q', 'sum(fb_engagement):Q']
	).interactive().add_selection(brush).transform_filter(brush)

	return fake_news_daily

# Showing Altair chart on the apps
fake_news_daily = graph1(df)

# Define second graph - Daily publication per domain name
@st.cache(allow_output_mutation=True)
def graph2(df):
	click_domain = alt.selection_multi(encodings=['color']) 
	daily_publi_per_domain = alt.Chart(df, title = 'Number of Facebook engagements per day per domain name').mark_point().encode(
    	x='published_date:T',
    	y='fb_engagement:Q',
    	color='Domain name:N',
    	tooltip=['published_date:T', 'title:N', 'fb_engagement:Q', 'category:N'] 
	).interactive().add_selection(brush).transform_filter(brush)

	return daily_publi_per_domain

# Showing Altair chart on the apps
daily_publi_per_domain = graph2(df)

st.altair_chart(fake_news_daily | daily_publi_per_domain, use_container_width=False)

st.write('## Impact of origins and categories')

# Create new dataset to show top 10 fake news by category
#@st.cache()
def top10_df(df):
	df_top10 = df.groupby(['category','title'])['fb_engagement'].sum().reset_index()
	df_top10['Rank'] = df_top10.groupby('category')['fb_engagement'].rank('dense', ascending = False)
	df_top10 = df_top10[df_top10['Rank'] <= 10]
	df_top10 = df_top10.sort_values(['category','Rank'], ascending = False)

	return df_top10

df_top10 = top10_df(df)

categories = list(df.category.unique())
category = st.sidebar.multiselect('Category', categories)
origins = list(df.Origin.unique())
origin = st.sidebar.multiselect('Origin', origins)
keys = dict()
keys['category'] = category
keys['Origin'] = origin

# Define fourth graph - Repartition of categories per origin
def graph4(df):
	if len(keys['Origin']) > 0:
		df = df[df['Origin'].isin(keys['Origin'])]
	cat_per_origin = alt.Chart(df, title = 'Detail of categories by origin').mark_bar().encode(
    	x=alt.X('Origin:N',sort ='-y'),
    	y=alt.Y('count(category):Q'),
    	color='category:N',
    	tooltip=['count(category):Q', 'category:N']
	).interactive().properties(width=800, height=400)

	return cat_per_origin

cat_per_origin = graph4(df)
st.write('In this section, the filters on the Category and Origin that can be found on the sidebar can be used to get specific information from the graphs.')
st.write('The graph below gives the relationship between the origins and the categories of fake news. ')
st.altair_chart(cat_per_origin)


def graph8(df):
	#all_category = df['category'].unique()
	#dropdown_cat = alt.binding_select(options= all_category)
	#select_category = alt.selection_single(fields=['category'], bind = dropdown_cat, name = 'Selector_test')
	if len(keys['category']) > 0:
		df = df[df['category'].isin(keys['category'])]
	nb_word_engagement_category = alt.Chart(df, title = 'Impact of the length of the title on the engagement on Facebook - Category').mark_bar().encode(
    	x=alt.X('Lenght of title:Q'),
    	y=alt.Y('mean(fb_engagement):Q',sort='x'),
    	color = alt.Color('mean(fb_engagement):Q',scale=alt.Scale(scheme='goldred')),
    	tooltip=['mean(fb_engagement):Q', 'count(titre):Q']
		).interactive()
		
	return nb_word_engagement_category

def graph9(df):
	if len(keys['Origin']) > 0:
		df = df[df['Origin'].isin(keys['Origin'])]
	nb_word_engagement_origin = alt.Chart(df, title = 'Impact of the length of the title on the engagement on Facebook - Origin').mark_bar().encode(
    	x=alt.X('Lenght of title:Q'),
    	y=alt.Y('mean(fb_engagement):Q',sort='x'),
    	color = alt.Color('mean(fb_engagement):Q',scale=alt.Scale(scheme='goldred')),
    	tooltip=['mean(fb_engagement):Q', 'count(titre):Q']
		).interactive()

	return nb_word_engagement_origin

st.write('The two graphs below show the impact of the lenght of the artcile titles on the Facebook engagement, grouped by category [left], or origin [right].')
nb_word_engagement_cat = graph8(df)
nb_word_engagement_origin = graph9(df)

st.altair_chart(nb_word_engagement_cat | nb_word_engagement_origin)


def graph10(df):
	click_day_of_week = alt.selection_multi(encodings=['color'])
	daysofweek = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]
	if len(keys['category']) > 0:
		df = df[df['category'].isin(keys['category'])]
	fake_news_DoW_cat = alt.Chart(df, title = 'Number of publication per day of the week - Category').mark_point().encode(
	    x=alt.X('Day of the week:N',sort=daysofweek),
	    y=alt.Y('count(titre):Q'),
	    color=alt.Color('Day of the week:N', sort = daysofweek),
	    tooltip=['count(titre):Q','sum(fb_engagement):Q']
	).interactive()

	return fake_news_DoW_cat

def graph11(df):
	click_day_of_week = alt.selection_multi(encodings=['color'])
	daysofweek = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]
	if len(keys['Origin']) > 0:
		df = df[df['Origin'].isin(keys['Origin'])]
	fake_news_DoW_org = alt.Chart(df, title = 'Number of publication per day of the week - Origin').mark_point().encode(
	    x=alt.X('Day of the week:N',sort=daysofweek),
	    y=alt.Y('count(titre):Q'),
	    color=alt.Color('Day of the week:N', sort = daysofweek),
	    tooltip=['count(titre):Q','sum(fb_engagement):Q']
	).interactive()

	return fake_news_DoW_org

st.write('Fake news are not published at the same frequency throughout the weeks. The graphs below show the relationship between day of the week and number of fake news published, grouped by category [left] and origin [right].')
fake_news_DoW_cat = graph10(df)
fake_news_DoW_org = graph11(df)

st.altair_chart(fake_news_DoW_cat | fake_news_DoW_org)

# Create new df to get the top 10 articles by origin per month (ranking)
def df_engagement_month_origin(df):
	df_engagement_month_origin = df.groupby(['Origin','month_int', 'category'])['fb_engagement'].sum().reset_index()
	df_engagement_month_origin['Rank'] = df_engagement_month_origin.groupby('month_int')['fb_engagement'].rank('dense', ascending = False)
	df_engagement_month_origin = df_engagement_month_origin[df_engagement_month_origin['Rank'] <= 10]
	df_engagement_month_origin = df_engagement_month_origin.sort_values('month_int')

	return df_engagement_month_origin

df_engagement_month_origin = df_engagement_month_origin(df)

# Create new df to get the top 10 articles by category per month (ranking)
def df_engagement_month_category(df):
	df_engagement_month_category = df.groupby(['category','month_int', 'Origin'])['fb_engagement'].sum().reset_index()
	df_engagement_month_category['Rank'] = df_engagement_month_category.groupby('month_int')['fb_engagement'].rank('dense', ascending = False)
	df_engagement_month_category = df_engagement_month_category[df_engagement_month_category['Rank'] <= 10]
	df_engagement_month_category = df_engagement_month_category.sort_values('month_int')

	return df_engagement_month_category

df_engagement_month_category = df_engagement_month_category(df)

month_slider = alt.binding_range(min=1, max=12, step=1, name='Month of the year:')
slider_selection_month = alt.selection_single(bind=month_slider, fields=['month_int'], name='slider')
click_cat_orig = alt.selection_multi(encodings=['color'])

st.write("## Relationships between origins and categories by month")

# Define fifth graph - Daily fake news publications
def graph5(df,month_slider,slider_selection_month,click_cat_orig):
	# fake_news_daily
	fake_news_daily = alt.Chart(df, title = 'Sum of Facebook engement per Origin').mark_point().encode(
    	x=alt.X('yearmonthdate(published_date):T', title = 'Day of publication'),
    	y=alt.Y('count(titre):Q'),
    	color=alt.Color('sum(fb_engagement)',scale=alt.Scale(scheme='goldred')),
    	tooltip=['published_date:T', 'sum(fb_engagement):Q']
	).add_selection(
    	slider_selection_month
	).transform_filter(
    	slider_selection_month)
	fake_news_daily = fake_news_daily.add_selection(click_cat_orig).transform_filter(click_cat_orig)

	return fake_news_daily

# Define sixth graph - Top 10 engagement per origin per month
def graph6(df_engagement_month_origin, month_slider,slider_selection_month,click_cat_orig):
	engagement_per_origin = alt.Chart(df_engagement_month_origin, title = 'Sum of Facebook engement per Category').mark_bar().encode(
    	x='sum(fb_engagement):Q',
    	y=alt.Y('Origin:N',sort='-x'),
    	color=alt.Color('Origin:N',legend = None),
    	tooltip=['sum(fb_engagement):Q', 'count(title):Q']
	).interactive().add_selection(click_cat_orig).transform_filter(click_cat_orig)
	engagement_per_origin = engagement_per_origin.add_selection(slider_selection_month).transform_filter(slider_selection_month)

	return engagement_per_origin

# Define seventh graph - Top 10 engagement per category per month
def graph7(df_engagement_month_category,month_slider,slider_selection_month,click_cat_orig):
	engagement_per_category = alt.Chart(df_engagement_month_category, title = 'Number of publication per day and Facebook engagement').mark_bar().encode(
   		x='sum(fb_engagement):Q',
    	y=alt.Y('category:N',sort='-x'),
    	color = alt.Color('category:N',legend = None),
    	tooltip=['sum(fb_engagement):Q', 'count(title):Q']
	).interactive().add_selection(click_cat_orig).transform_filter(click_cat_orig)
	engagement_per_category = engagement_per_category.add_selection(slider_selection_month).transform_filter(slider_selection_month)

	return engagement_per_category

fake_news_daily = graph5(df,month_slider,slider_selection_month,click_cat_orig)
engagement_per_origin = graph6(df_engagement_month_origin,month_slider,slider_selection_month,click_cat_orig)
engagement_per_category = graph7(df_engagement_month_category,month_slider,slider_selection_month,click_cat_orig)
st.write('In this section, the 3 plots are interconnected. The slider at the bottom can be used to change the month, and the categories and origins on the top graphs can be clicked on to filter out information.')
st.write('These plots show the Facebook engagement on fake news articles throught the year. It is possible to group the articles by category [top left] or origin [top right]. It is also possible to view the amount of engagement per day [bottom].')
st.altair_chart((engagement_per_origin | engagement_per_category) & fake_news_daily)