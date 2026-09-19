import os

from flask import Flask, render_template, request, redirect, url_for, send_file

from database import init_db, save_trip, get_trips, get_trip, delete_trip


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

app = Flask(
    __name__,
    template_folder=TEMPLATES_DIR
)

print("===================================")
print("ЗАПУЩЕННЫЙ ФАЙЛ:", os.path.abspath(__file__))
print("ПАПКА ШАБЛОНОВ:", TEMPLATES_DIR)
print("ИСТОРИЯ СУЩЕСТВУЕТ:", os.path.exists(os.path.join(TEMPLATES_DIR, "history.html")))
print("ФАЙЛЫ В TEMPLATES:", os.listdir(TEMPLATES_DIR))
print("===================================")

app = Flask(__name__)

# Инициализируем базу данных
init_db()


def get_number(name):
    value = request.form.get(name, "0")

    try:
        number = float(value.replace(",", "."))

        if number < 0:
            return 0

        return number

    except (ValueError, AttributeError):
        return 0

@app.route("/apple-touch-icon.png")
def apple_touch_icon():
    return send_file(
        "static/icons/icon-180.png",
        mimetype="image/png"
    )


@app.route("/apple-touch-icon-120x120.png")
def apple_touch_icon_120():
    return send_file(
        "static/icons/icon-180.png",
        mimetype="image/png"
    )


@app.route("/apple-touch-icon-120x120-precomposed.png")
def apple_touch_icon_precomposed():
    return send_file(
        "static/icons/icon-180.png",
        mimetype="image/png"
    )

@app.route("/", methods=["GET", "POST"])
def home():

    result = None

    if request.method == "POST":

        # -----------------------------
        # ОСНОВНЫЕ ДАННЫЕ
        # -----------------------------

        route = request.form.get("route", "").strip()

        distance = get_number("distance")
        return_percent = get_number("return_percent")
        rate = get_number("rate")
        target_margin = get_number("target_margin")
        monthly_distance = get_number("monthly_distance")

        # -----------------------------
        # ТОПЛИВО
        # -----------------------------

        consumption = get_number("consumption")
        fuel_price = get_number("fuel_price")

        # -----------------------------
        # ПЕРЕМЕННЫЕ РАСХОДЫ
        # -----------------------------

        driver_per_km = get_number("driver_per_km")
        repair_per_km = get_number("repair_per_km")
        tires_per_km = get_number("tires_per_km")
        depreciation_per_km = get_number("depreciation_per_km")

        # -----------------------------
        # ПОСТОЯННЫЕ РАСХОДЫ
        # -----------------------------

        osago = get_number("osago")
        kasko = get_number("kasko")
        tax = get_number("tax")
        leasing = get_number("leasing")
        parking = get_number("parking")
        washing = get_number("washing")
        dispatcher = get_number("dispatcher")

        # -----------------------------
        # ПРОЧИЕ РАСХОДЫ
        # -----------------------------

        toll = get_number("toll")
        loading = get_number("loading")
        other = get_number("other")

        # ==================================================
        # РАСЧЁТ
        # ==================================================

        return_distance = distance * return_percent / 100

        total_distance = distance + return_distance

        liters = total_distance * consumption / 100

        fuel_cost = liters * fuel_price

        driver_cost = total_distance * driver_per_km

        repair_cost = total_distance * repair_per_km

        tires_cost = total_distance * tires_per_km

        depreciation_cost = total_distance * depreciation_per_km

        # -----------------------------
        # ПОСТОЯННЫЕ РАСХОДЫ
        # -----------------------------

        monthly_fixed_cost = (
            osago
            + kasko
            + tax
            + leasing
            + parking
            + washing
            + dispatcher
        )

        if monthly_distance > 0:
            fixed_per_km = monthly_fixed_cost / monthly_distance
        else:
            fixed_per_km = 0

        fixed_cost = total_distance * fixed_per_km

        # -----------------------------
        # ОБЩАЯ СЕБЕСТОИМОСТЬ
        # -----------------------------

        total_cost = (
            fuel_cost
            + driver_cost
            + repair_cost
            + tires_cost
            + depreciation_cost
            + fixed_cost
            + toll
            + loading
            + other
        )

        # -----------------------------
        # ВЫРУЧКА
        # -----------------------------

        revenue = distance * rate

        # -----------------------------
        # ПРИБЫЛЬ
        # -----------------------------

        profit = revenue - total_cost

        # -----------------------------
        # СЕБЕСТОИМОСТЬ 1 КМ
        # -----------------------------

        if distance > 0:
            cost_per_km = total_cost / distance
        else:
            cost_per_km = 0

        # -----------------------------
        # МАРЖА
        # -----------------------------

        if revenue > 0:
            margin = profit / revenue * 100
        else:
            margin = 0

        # -----------------------------
        # МИНИМАЛЬНАЯ СТАВКА
        # -----------------------------

        minimum_rate = cost_per_km

        # -----------------------------
        # ЦЕЛЕВАЯ СТАВКА
        # -----------------------------

        if 0 <= target_margin < 100:
            target_rate = minimum_rate / (1 - target_margin / 100)
        else:
            target_rate = 0

        # -----------------------------
        # ПРОГНОЗ
        # -----------------------------

        target_revenue = distance * target_rate

        target_profit = target_revenue - total_cost

        # -----------------------------
        # ЗАПАС ПО СТАВКЕ
        # -----------------------------

        rate_reserve = rate - minimum_rate

        # ==================================================
        # ДОЛИ РАСХОДОВ
        # ==================================================

        if total_cost > 0:

            fuel_percent = fuel_cost / total_cost * 100
            driver_percent = driver_cost / total_cost * 100
            repair_percent = repair_cost / total_cost * 100
            tires_percent = tires_cost / total_cost * 100
            depreciation_percent = depreciation_cost / total_cost * 100
            fixed_percent = fixed_cost / total_cost * 100
            toll_percent = toll / total_cost * 100
            loading_percent = loading / total_cost * 100
            other_percent = other / total_cost * 100

        else:

            fuel_percent = 0
            driver_percent = 0
            repair_percent = 0
            tires_percent = 0
            depreciation_percent = 0
            fixed_percent = 0
            toll_percent = 0
            loading_percent = 0
            other_percent = 0

        # ==================================================
        # СТАТУС
        # ==================================================

        if profit < 0:

            status = "УБЫТОЧНЫЙ РЕЙС"
            status_class = "danger"

        elif margin < 10:

            status = "НИЗКАЯ МАРЖА"
            status_class = "warning"

        else:

            status = "ПРИБЫЛЬНЫЙ РЕЙС"
            status_class = "success"

        # ==================================================
        # ОБРАТНЫЙ ПРОБЕГ
        # ==================================================

        if total_distance > 0:

            empty_distance_percent = (
                return_distance / total_distance * 100
            )

        else:

            empty_distance_percent = 0

        # ==================================================
        # ТОПЛИВО НА ФАКТИЧЕСКИЙ КМ
        # ==================================================

        if total_distance > 0:

            fuel_cost_per_actual_km = (
                fuel_cost / total_distance
            )

        else:

            fuel_cost_per_actual_km = 0

        # ==================================================
        # РЕЗУЛЬТАТ
        # ==================================================

        result = {

            "route": route,

            "distance": distance,

            "return_distance": return_distance,

            "total_distance": total_distance,

            "empty_distance_percent": empty_distance_percent,

            "liters": liters,

            "fuel_cost": fuel_cost,

            "fuel_cost_per_actual_km": fuel_cost_per_actual_km,

            "driver_cost": driver_cost,

            "repair_cost": repair_cost,

            "tires_cost": tires_cost,

            "depreciation_cost": depreciation_cost,

            "fixed_cost": fixed_cost,

            "toll": toll,

            "loading": loading,

            "other": other,

            "total_cost": total_cost,

            "revenue": revenue,

            "profit": profit,

            "cost_per_km": cost_per_km,

            "margin": margin,

            "rate": rate,

            "minimum_rate": minimum_rate,

            "target_margin": target_margin,

            "target_rate": target_rate,

            "target_revenue": target_revenue,

            "target_profit": target_profit,

            "rate_reserve": rate_reserve,

            "fuel_percent": fuel_percent,

            "driver_percent": driver_percent,

            "repair_percent": repair_percent,

            "tires_percent": tires_percent,

            "depreciation_percent": depreciation_percent,

            "fixed_percent": fixed_percent,

            "toll_percent": toll_percent,

            "loading_percent": loading_percent,

            "other_percent": other_percent,

            "status": status,

            "status_class": status_class
        }

        # ==================================================
        # СОХРАНЕНИЕ РЕЙСА
        # ==================================================

        trip_data = {

            "route": route,

            "distance": distance,
            "return_percent": return_percent,
            "rate": rate,
            "target_margin": target_margin,
            "monthly_distance": monthly_distance,

            "consumption": consumption,
            "fuel_price": fuel_price,

            "driver_per_km": driver_per_km,
            "repair_per_km": repair_per_km,
            "tires_per_km": tires_per_km,
            "depreciation_per_km": depreciation_per_km,

            "osago": osago,
            "kasko": kasko,
            "tax": tax,
            "leasing": leasing,
            "parking": parking,
            "washing": washing,
            "dispatcher": dispatcher,

            "toll": toll,
            "loading": loading,
            "other": other,

            "return_distance": return_distance,
            "total_distance": total_distance,
            "liters": liters,

            "fuel_cost": fuel_cost,
            "driver_cost": driver_cost,
            "repair_cost": repair_cost,
            "tires_cost": tires_cost,
            "depreciation_cost": depreciation_cost,
            "fixed_cost": fixed_cost,
            "total_cost": total_cost,

            "revenue": revenue,
            "profit": profit,
            "cost_per_km": cost_per_km,
            "margin": margin,

            "minimum_rate": minimum_rate,
            "target_rate": target_rate,
            "target_revenue": target_revenue,
            "target_profit": target_profit,
            "rate_reserve": rate_reserve
        }

        save_trip(trip_data)

    return render_template(
        "index.html",
        result=result
    )


# ==========================================================
# ИСТОРИЯ РЕЙСОВ
# ==========================================================

@app.route("/history")
def history():

    trips = get_trips()

    return render_template(
        "history.html",
        trips=trips
    )


# ==========================================================
# ПРОСМОТР ОДНОГО РЕЙСА
# ==========================================================

@app.route("/history/<int:trip_id>")
def history_detail(trip_id):

    trip = get_trip(trip_id)

    if trip is None:
        return "Рейс не найден", 404

    return render_template(
        "history_detail.html",
        trip=trip
    )


# ==========================================================
# УДАЛЕНИЕ РЕЙСА
# ==========================================================

@app.route("/history/delete/<int:trip_id>", methods=["POST"])
def history_delete(trip_id):

    delete_trip(trip_id)

    return redirect(url_for("history"))


if __name__ == "__main__":

    app.run(
        host="192.168.1.178",
        port=5000,
        debug=True
    )