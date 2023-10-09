# -*- coding: utf-8 -*-
"""
Created on Mon Oct  9 11:17:59 2023

@author: SemanurSancar
"""


import requests
import json
import pandas as pd



def hourly_typical_meteorological_year (lat, lon):

    # GET isteği yapacağımız URL'yi belirtiyoruz
    url = 'https://re.jrc.ec.europa.eu/api/tmy?lat={}&lon={}&outputformat=json'.format(lat, lon)
    
    # GET isteğini gönderiyoruz
    response = requests.get(url)
    
    # Yanıtı kontrol ediyoruz
    if response.status_code == 200:
        # Yanıtın içeriğini alıyoruz
        content = response.text
    
        # İçeriği yazdırıyoruz
        # print(content)
    else:
        print('İstek başarısız oldu. Hata kodu:', response.stat.us_code)
    
    # Metin verisini JSON formatına dönüştürüyoruz
    data = json.loads(content)
    # data = content    
    # # 'outputs' ve 'monthly' verilerini alıyoruz
    outputs_hourly = pd.DataFrame(data['outputs']['tmy_hourly'])


    
    # # DataFrame oluşturmak için verileri düzenliyoruz
    # df = pd.DataFrame(outputs_hourly)

    # table = df[["month","E_m", "SD_m"]]

    # years
    year_min = data['inputs']['meteo_data']['year_min']
    year_max = data['inputs']['meteo_data']['year_max']

    note = "The data includes the average of {} and {}.".format(year_min, year_max)    
    

    

    return outputs_hourly, note

def power_calculator(wind_speed_hourly, height, swept_area):
    
    # V2 = V1 * (h2/h1)^alfa
    # V1 = Başlangıç yüksekliği (örn. 10 m) için bilinen rüzgar hızı
    # V2 = Tahmin edilmek istenen yükseklikte (örn. 80 m) olan rüzgar hızı
    # h1 = Başlangıç yüksekliği (örn. 10 m)
    # h2 = Tahmin edilmek istenen yükseklik (örn. 80 m)
    # alfa = Karasal (kara üstü) alanlar için genellikle 0.143 değerini alır.
    
    wind_speed_hourly[f"WS{height}m"] = wind_speed_hourly["WS10m"] * (height/10)**(0.143)
    
    # P=0.5*ρ*A*V^3*Cp
    # ρ = Hava yoğunluğu (ortalama deniz seviyesinde yaklaşık 1.225 kg/m^3)
    # A = Türbinin kanatlarının süpürdüğü alan =  pi * kanat_uzunlugu^2
    # V = Rüzgar hızı (80 m yükseklik için hesaplanan hız)
    # Cp= Güç katsayısı (teorik maksimum değeri 0.59'dur, ama gerçekte bu değer türbine göre değişir ve genellikle 0.35-0.45 arasında bir değeri vardır).
    
    power_generation_hourly = pd.DataFrame(0.5*1.225*swept_area*(wind_speed_hourly[f"WS{height}m"]**3)*0.45)
    power_generation_hourly.rename(columns={f"WS{height}m":f"P{height}m"}, inplace=True)
    
    
    return power_generation_hourly
    


def monthly_wind_generation(lat, lon, height, swept_area):
    
    outputs_hourly, user_note = hourly_typical_meteorological_year(lat, lon)
    
    outputs_hourly["datetime"] = pd.to_datetime(outputs_hourly["time(UTC)"], format='%Y%m%d:%H%M')
    
    
    wind_speed_hourly = pd.DataFrame(outputs_hourly["WS10m"])
    
    
    
    power_generation_hourly = power_calculator(wind_speed_hourly, height, swept_area)
    
    power_generation_hourly["datetime"] = pd.to_datetime(outputs_hourly["datetime"], format='%Y%m%d:%H%M')
    
    
    # Ay bazında grupla ve P80m sütununu topla
    result =     power_generation_hourly.groupby(power_generation_hourly['datetime'].dt.to_period('M'))[f"P{height}m"].sum().reset_index()
    result['datetime'] = result['datetime'].dt.to_timestamp()  # Ayın başlangıç tarihini datetime olarak döndür
    
    # # Aylar ve yıllara göre sırala
    # result = result.sort_values(by=[result['datetime'].dt.month, result['datetime'].dt.year], inplace=True)
    
    
    # Ay ve yıl bilgilerini geçici sütunlara ekleyin
    result['Months'] = result['datetime'].dt.month
    result['year'] = result['datetime'].dt.year
    
    # Aylar ve yıllara göre sırala
    result = result.sort_values(by=['Months', 'year'])
    
    wind_generation_monthly = result[["Months", f"P{height}m"]]
    
    wind_generation_monthly.rename(columns={f"P{height}m":f"E{height}m [kWh]"}, inplace=True)
    
    return wind_generation_monthly, user_note


# lat = 37.019148
# lon = 36.116237
# height = 80
# swept_area = 300

# table, user_note = monthly_wind_generation(lat, lon, height, swept_area)

# print(table)
