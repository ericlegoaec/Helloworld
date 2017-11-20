
# coding: utf-8

# In[1]:

import pandas as pd
import numpy as np
from pandas import ExcelWriter
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties, FontManager
import seaborn as sns
from jinja2 import Template
import win32com.client
import os
import glob
from datetime import datetime
import dateutil
# %matplotlib inline


# In[3]:

send_email_option = False
email_template_file_path = 'email_template.html'
broker_list_file_path = 'broker_list.csv'
summary_file_folder = "\\\\p7fs0003\\nd\\3033-Horizon-FA-Share\\Horizon_daily_reports\\brokerPnL\\input\\"
output_file_path = 'output\\output.xlsx'
chart_file_path = 'output\\charts.png'
preview_file_path = 'output\\email_preview.html'


# In[4]:

broker_list = pd.read_csv(broker_list_file_path, encoding='hkscs')
broker_list = broker_list.set_index('Long Name')['Short Name'].to_dict()


# In[5]:

latest_summary_file = max(glob.iglob('{}*.xls'.format(summary_file_folder)), key=os.path.getctime)


# In[6]:

file_name_date = datetime(*map(int, latest_summary_file.replace(summary_file_folder,'').replace('.xls', '').split('_')[2:]))


# In[7]:

file_creation_date = datetime.fromtimestamp(os.path.getctime(latest_summary_file))
if file_name_date.date() != file_creation_date.date():
    raise ValueError('File name date not match the creation date')


# In[8]:

df = pd.read_html(latest_summary_file, encoding='hkscs')[0]

df.columns = df.ix[0]
df = df.ix[1:]
df['OUR_BUY_AVG_PRICE'] = df['OUR_BUY_AVG_PRICE'].astype(float)
df['OUR_SELL_AVG_PRICE'] = df['OUR_SELL_AVG_PRICE'].astype(float)
df['OUR_BUY_QUANTITY'] = df['OUR_BUY_QUANTITY'].astype(float)
df['OUR_SELL_QUANTITY'] = df['OUR_SELL_QUANTITY'].astype(float)
df['OUR_TOT_CONSIDERATION'] = df['OUR_TOT_CONSIDERATION'].astype(float)


# In[9]:

df['Broker'] = df['BROKER_NAME'].apply(lambda b: broker_list.get(str(b).replace('\ue05e', '滙'), b))
df['PnL'] = np.min(df[['OUR_BUY_QUANTITY','OUR_SELL_QUANTITY']], axis=1) * (df['OUR_BUY_AVG_PRICE'] - df['OUR_SELL_AVG_PRICE'])
df['Portfolio'] = df['PRODUCTID'].apply(lambda p: 'CBBC Trading' if p[0] == '6' else 'Warrant Trading')


# In[10]:

def make_portfolio_data(portfolio):
    df_filter = (df['Portfolio'] == portfolio) & (df['Broker'] != 'INTERNAL') & (df['Broker'] != 'Internal')
    pivot = df.ix[df_filter].pivot_table(
        values=['OUR_TOT_CONSIDERATION', 'PnL'], index='Broker', aggfunc='sum')
    pivot.columns = ['Turnover (HKD)', 'PnL (HKD)']
    pivot = pivot.sort_values('Turnover (HKD)', ascending=False)

    plot_pivot = pivot.iloc[0:7]
    plot_pivot = (plot_pivot
                  .append(pd.DataFrame({
                    'Turnover (HKD)': pivot['Turnover (HKD)'].sum() - plot_pivot['Turnover (HKD)'].sum(),
                    'PnL (HKD)': pivot['PnL (HKD)'].sum() - plot_pivot['PnL (HKD)'].sum()
                }, index=['Others']))
                  .reset_index()
                  .rename(columns={'index': 'Broker', 'Turnover (HKD)': 'Turnover', 'PnL (HKD)': 'PnL'})
                 )
    
    total_turnover = pivot['Turnover (HKD)'].sum()
    total_pnl = pivot['PnL (HKD)'].sum()
    pivot_to_display = pd.concat([pivot, pd.DataFrame({
                'Turnover (HKD)': total_turnover,
                'PnL (HKD)': total_pnl
            }, index=['Total'])])
    pivot_to_display['(bps)'] = pivot_to_display['PnL (HKD)'] / pivot_to_display['Turnover (HKD)'] * 10000
    
    return pivot, pivot_to_display, plot_pivot


# In[11]:

portfolios = ['Warrant Trading', 'CBBC Trading']
portfolio_data = {portfolio: make_portfolio_data(portfolio) for portfolio in portfolios}


# In[ ]:

excel_writer = ExcelWriter(output_file_path)

for portfolio, (pivot, pivot_to_display, plot_pivot) in portfolio_data.items():
    pivot.to_excel(excel_writer, '{} pivot'.format(portfolio))
    pivot_to_display.to_excel(excel_writer, '{} pivot'.format(portfolio))
    plot_pivot.to_excel(excel_writer, '{} plot_pivot'.format(portfolio))

excel_writer.save()


# In[ ]:

with sns.axes_style('dark', {'font.family': ['SimHei'], 'axes.grid': False}):
    fig, axes = plt.subplots(ncols=2)
    fig.set_figheight(5)
    fig.set_figwidth(15)
    
    for portfolio, ax in zip(portfolios, axes):
        
        _, _, plot_pivot = portfolio_data[portfolio]
    
        sns.barplot(x='Broker', y='Turnover', data=plot_pivot, ax=ax)
        ax.set_yticklabels([])
        ax.set_ylim(100)
        ax.set_ylabel('')
        ax.set_title('{} Turnover'.format(portfolio))

        for bar, p in zip(ax.patches, plot_pivot['Turnover'] / plot_pivot['Turnover'].sum()):
            x = bar.xy[0] + bar.get_width() / 4
            y = bar.get_height() / 2
            ax.text(x, y, '{:.0f} %'.format(p*100))


# In[ ]:

fig.savefig(chart_file_path, dpi=100)


# In[ ]:

with open(email_template_file_path) as f:
    html_template = (''.join(f.readlines()))

template = Template(html_template)
html_report = template.render(
    today=file_name_date.strftime('%Y-%m-%d'),
    warrants_total_turnover='{:,.0f}'.format(portfolio_data['Warrant Trading'][0]['Turnover (HKD)'].sum()),
    cbbc_total_turnover='{:,.0f}'.format(portfolio_data['CBBC Trading'][0]['Turnover (HKD)'].sum()),
    warrants_turnover_table=portfolio_data['Warrant Trading'][1].applymap(lambda x: '{:,.0f}'.format(x)).to_html(),
    cbbc_turnover_table=portfolio_data['CBBC Trading'][1].applymap(lambda x: '{:,.0f}'.format(x)).to_html(),
    source_file=latest_summary_file
)


# In[ ]:

from IPython.display import display, HTML
display(HTML(html_report))

with open(preview_file_path, 'w', encoding='hkscs') as f:
    f.write(html_report)
    print('Report available for preview at "{}"'.format(os.path.join(os.getcwd(), f.name)))


# In[ ]:

receipients = list(pd.read_csv('receipient_list.txt')['email_address'])
def send_email():
    olMailItem = 0x0
    obj = win32com.client.Dispatch("Outlook.Application")
    newMail = obj.CreateItem(olMailItem)
    newMail.Subject = "[TEST] HTI Warrants brokers distribution {}".format(file_name_date.strftime('%Y%m%d'))
    newMail.To = ";".join(receipients)
    newMail.HTMLBody  = html_report
    attachment1 = os.path.join(os.getcwd(), chart_file_path)
    newMail.Attachments.Add(attachment1)
    newMail.Send()
    print('Sent email to the following {} address(es): \n {}? \n'
         .format(len(receipients), receipients))


# In[ ]:

def ask_send_email():
    return input('Confirm send email to the following {} address(es) (y/n): \n {}? \n'
         .format(len(receipients), receipients)).lower() == 'y'

def is_send_email():
    if send_email_option is None:
        return ask_send_email()
    else:
        return send_email_option


# In[ ]:

if is_send_email():
    send_email()

