#!/usr/bin/env python
# coding: utf-8

# # Atliq Hotels Data Analysis Project

# In[1]:


import pandas as pd


# ### ==> 1. Data Import and Data Exploration

# Reading Bookings Data in a Dataframe and exploring it

# In[4]:


df_bookings = pd.read_csv("datasets/fact_bookings.csv")
df_bookings.head(5)


# In[5]:


df_bookings.shape


# In[6]:


df_bookings.room_category.unique()


# In[7]:


df_bookings.booking_platform.unique()


# In[8]:


df_bookings.booking_platform.value_counts()


# In[11]:


df_bookings.booking_platform.value_counts().plot(kind = "barh")


# In[12]:


df_bookings.describe()


# In[13]:


df_bookings.revenue_generated.min(), df_bookings.revenue_generated.max()


# Reading rest of the files

# In[14]:


df_date = pd.read_csv("datasets/dim_date.csv")
df_hotels = pd.read_csv("datasets/dim_hotels.csv")
df_rooms = pd.read_csv("datasets/dim_rooms.csv")
df_agg_bookings = pd.read_csv("datasets/fact_aggregated_bookings.csv")


# In[15]:


df_hotels.shape


# In[16]:


df_hotels.head(4)


# In[17]:


df_hotels.category.value_counts()


# In[21]:


df_hotels.city.value_counts().sort_values().plot(kind = "barh")


# Exploring the aggregate bookings

# In[22]:


df_agg_bookings.head(3)


# Finding out the unique property ids in aggregate bookings dataset

# In[23]:


df_agg_bookings.property_id.unique()


# Finding out total bookings per property_id

# In[24]:


df_agg_bookings.groupby("property_id")["successful_bookings"].sum()


# Finding out the days on which the bookings are greater than capacity

# In[25]:


df_agg_bookings[df_agg_bookings.successful_bookings>df_agg_bookings.capacity]


# Finding out properties that have the highest capacity

# In[26]:


df_agg_bookings.capacity.max()


# In[27]:


df_agg_bookings[df_agg_bookings.capacity==df_agg_bookings.capacity.max()]


# ### ==> 2. Data Cleaning

# In[28]:


df_bookings.describe()


# (1) Cleaning Invalid Guests

# In[29]:


df_bookings[df_bookings.no_guests<=0]


#  ### As we can see above, number of guests having less than zero value represents data error. We can ignore these records.

# In[31]:


df_bookings = df_bookings[df_bookings.no_guests>0]


# In[32]:


df_bookings.shape


# (2) Outlier removal in revenue generated 

# In[34]:


df_bookings.revenue_generated.min(), df_bookings.revenue_generated.max()


# In[35]:


df_bookings.revenue_generated.mean(), df_bookings.revenue_generated.median()


# In[36]:


avg, std = df_bookings.revenue_generated.mean(), df_bookings.revenue_generated.std()


# In[37]:


higher_limit = avg + 3*std
higher_limit


# In[38]:


lower_limit = avg - 3*std
lower_limit


# In[39]:


df_bookings[df_bookings.revenue_generated<=0]


# In[40]:


df_bookings[df_bookings.revenue_generated>higher_limit]


# In[41]:


df_bookings = df_bookings[df_bookings.revenue_generated<=higher_limit]
df_bookings.shape


# In[42]:


df_bookings.revenue_realized.describe()


# In[43]:


higher_limit = df_bookings.revenue_realized.mean() + 3*df_bookings.revenue_realized.std()
higher_limit


# In[44]:


df_bookings[df_bookings.revenue_realized>higher_limit]


# One observation we can have in above dataframe is that all rooms are RT4 which means presidential suit. Now since RT4 is a luxurious room it is likely their rent will be higher. To make a fair analysis, we need to do data analysis only on RT4 room types

# In[45]:


df_bookings[df_bookings.room_category=="RT4"].revenue_realized.describe()


# In[46]:


# Higher limit would be mean + 3* standard deviation

23439 + 3*9048


# Here higher limit comes to be 50583 and in our dataframe above we can see that max value for revenue realized is 45220. Hence we can conclude that there is no outlier and we don't need to do any data cleaning on this particular column.

# In[47]:


df_bookings[df_bookings.booking_id=="May012216558RT213"]


# In[48]:


df_bookings.isnull().sum()


# Total values in our dataframe is 134576. Out of that 77899 rows has null rating. Since there are many rows with null rating, we should not filter these values. Also we should not replace this rating with a median or mean rating etc

# ### Finding null value in the columns of aggregate booking

# In[49]:


df_agg_bookings.isnull().sum()


# In[50]:


df_agg_bookings[df_agg_bookings.capacity.isna()]


# In[51]:


df_agg_bookings.capacity.median()


# Filling the null values with the median value in aggregate bookings.

# In[52]:


df_agg_bookings.capacity.fillna(df_agg_bookings.capacity.median(), inplace=True)


# In[53]:


df_agg_bookings.loc[[8,15]]


# Finding out the records in aggregate bookings that have successful_bookings value greater than capacity. I will filter those records

# In[54]:


df_agg_bookings[df_agg_bookings.successful_bookings>df_agg_bookings.capacity]


# In[55]:


df_agg_bookings.shape


# In[56]:


df_agg_bookings = df_agg_bookings[df_agg_bookings.successful_bookings<=df_agg_bookings.capacity]
df_agg_bookings.shape


# ### ==> 3. Data Transformation

# I will be creating occupancy percentage column

# In[57]:


df_agg_bookings.head(3)


# In[59]:


df_agg_bookings['occ_pct'] = df_agg_bookings.apply(lambda row: row['successful_bookings']/row['capacity'], axis=1)


# In[60]:


new_col = df_agg_bookings.apply(lambda row: row['successful_bookings']/row['capacity'], axis=1)
df_agg_bookings = df_agg_bookings.assign(occ_pct=new_col.values)
df_agg_bookings.head(3)


# Converting it to a percentage value

# In[61]:


df_agg_bookings['occ_pct'] = df_agg_bookings['occ_pct'].apply(lambda x: round(x*100, 2))
df_agg_bookings.head(3)


# In[62]:


df_bookings.head()


# In[63]:


df_agg_bookings.info()


# ### ==> 3. Insights Generation

# 1) Calculating the average occupancy rate in each of the room categories.

# In[64]:


df_agg_bookings.head(3)


# In[65]:


df_agg_bookings.groupby("room_category")["occ_pct"].mean()


# The original dataset included room types as variables like RT1, RT2, etc. Since, these variables lack business interpretability which makes it difficult to derive meaningful insights, I will print room categories such as Standard, Premium, Elite, etc along with average occupancy percentage

# In[66]:


df = pd.merge(df_agg_bookings, df_rooms, left_on="room_category", right_on="room_id")
df.head(4)


# In[67]:


df.drop("room_id",axis=1, inplace=True)
df.head(4)


# In[68]:


df.groupby("room_class")["occ_pct"].mean()


# In[69]:


df[df.room_class=="Standard"].occ_pct.mean()


# 2) Printing average occupancy rate per city

# In[70]:


df_hotels.head(3)


# In[71]:


df = pd.merge(df, df_hotels, on="property_id")
df.head(3)


# In[72]:


df.groupby("city")["occ_pct"].mean()


# 3) When was the occupancy better? Weekday or Weekend?

# In[73]:


df_date.head(3)


# In[74]:


df = pd.merge(df, df_date, left_on="check_in_date", right_on="date")
df.head(3)


# In[75]:


df.groupby("day_type")["occ_pct"].mean().round(2)


# 4) In the month of June, whatis the occupancy for the different cities?

# In[76]:


df_june_22 = df[df["mmm yy"]=="Jun 22"]
df_june_22.head(4)


# In[77]:


df_june_22.groupby('city')['occ_pct'].mean().round(2).sort_values(ascending=False)


# In[78]:


df_june_22.groupby('city')['occ_pct'].mean().round(2).sort_values(ascending=False).plot(kind="barh")


# 5) Appending the data for the month of August to the existing data

# In[79]:


df_august = pd.read_csv("datasets/new_data_august.csv")
df_august.head(3)


# In[80]:


df_august.columns


# In[81]:


df.columns


# In[82]:


df_august.shape


# In[83]:


df.shape


# In[84]:


latest_df = pd.concat([df, df_august], ignore_index = True, axis = 0)
latest_df.tail(10)


# In[85]:


latest_df.shape


# 6) Printing the revenue realized per city

# In[86]:


df_bookings.head()


# In[87]:


df_hotels.head(3)


# In[88]:


df_bookings_all = pd.merge(df_bookings, df_hotels, on="property_id")
df_bookings_all.head(3)


# In[89]:


df_bookings_all.groupby("city")["revenue_realized"].sum()


# 7) Printing month by month revenue

# In[90]:


df_date.head(3)


# In[91]:


df_date["mmm yy"].unique()


# In[92]:


df_bookings_all.head(3)


# In[93]:


df_date.info()


# In[94]:


df_date["date"] = pd.to_datetime(df_date["date"])
df_date.head(3)


# In[95]:


df_bookings_all.info()


# In[98]:


df_bookings_all["check_in_date"] = pd.to_datetime(df_bookings_all["check_in_date"], dayfirst=True, errors='coerce')
df_bookings_all.head(4)


# In[99]:


df_bookings_all = pd.merge(df_bookings_all, df_date, left_on="check_in_date", right_on="date")
df_bookings_all.head(3)


# In[100]:


df_bookings_all.groupby("mmm yy")["revenue_realized"].sum()


# 8) Printing revenue realized per hotel type

# In[101]:


df_bookings_all.property_name.unique()


# In[102]:


df_bookings_all.groupby("property_name")["revenue_realized"].sum().round(2).sort_values()


# 9. Printing average rating per city

# In[103]:


df_bookings_all.groupby("city")["ratings_given"].mean().round(2)


# 10. Printing a pie chart of revenue realized per booking platform

# In[104]:


df_bookings_all.groupby("booking_platform")["revenue_realized"].sum().plot(kind="pie")


# In[ ]:




