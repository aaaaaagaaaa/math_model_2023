import numpy as np
import math, random

## 以吸收塔为中心，正北方向为x轴，正东方向为y轴，垂直于地面为z轴
## 建立空间直角坐标系

# the cordinate of the heat absorber
absorber = np.array([0, 0, 76])

# latitude (degrees), north is positive
latitude = math.radians(39.4)

# altitude (km)
altitude = 3

# solar constant (kW/m2)
G_0 = 1.366

day_list = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

def D_delta(month):
    day_base = 31 + 28 + 21
    sum = 21
    for i in range(0, month - 1):
        sum += day_list[i]
    return sum - day_base

def D_omega(hour):
    return (hour - 12) * math.pi / 12

def angle_delta(month):
    D = D_delta(month)
    C = math.sin(2 * 23.45 * math.pi / 360)
    delta = C * math.sin(2 * math.pi * D / 365)
    return math.asin(delta)

def angle_alpha_s(month, hour):
    phi = latitude
    delta = angle_delta(month)
    omega = D_omega(hour)
    a1 = math.cos(delta) * math.cos(phi) * math.cos(omega)
    a2 = math.sin(delta) * math.sin(phi)
    return math.asin(a1 + a2)

def angle_gamma_s(month, hour):
    phi = latitude
    delta = angle_delta(month)
    alpha_s = angle_alpha_s(month, hour)
    a1 = math.sin(delta) - math.sin(alpha_s) * math.sin(phi)
    a2 = math.cos(alpha_s) * math.cos(phi)
    factor = a1 / a2
    if (factor <= -1):
        return math.pi
    else:
        return math.acos(a1 / a2)

class Mirror:

    # the default height of the mirrors
    default_height = 4

    eta_ref = 0.92

    neibour_distance = 3

    light_direct = np.array([0, 0, 1])

    light_DNI = 0

    def __init__(self, x, y, z = "default", length = 6, width = 6):
        if (z == "default"):
            newz = Mirror.default_height
        else:
            newz = z
        v = np.array([x, y, newz])
        self.cor = v
        self.norm = np.array([1, 0, 0])
        self.length = length
        self.width = width
        self.neibours = []

    def set_norm(self):
        """set the mirror's normal vector according to sunlight's direction"""
        v1 = absorber - self.cor
        v2 = Mirror.light_direct
        v1 /= np.linalg.norm(v1)
        v2 /= np.linalg.norm(v2)
        res = v1 + v2
        res /= np.linalg.norm(res)
        self.norm = res
        # Mirror.light_direct = sunlight.direct
        # Mirror.light_DNI = sunlight.DNI

    def d_HR(self):
        """distance between the mirror and the absorber"""
        return np.linalg.norm(absorber - self. cor)

    def eta_at(self):
        """atomspheric transmittance"""
        d = self.d_HR()
        if d <= 1000:
            return 0.99321 - 1.176e-4 * d + 1.97e-8 * d**2
        else:
            return 0

    def eta_cos(self):
        """cosine efficience"""
        d = absorber - self.cor
        normd = d / np.linalg.norm(d)
        return np.dot(self.norm, normd)

    def add_to_list(self, mlist):
        for m in mlist:
            d = np.linalg.norm(self.cor - m.cor)
            if d <= Mirror.neibour_distance:
                self.neibours.append(m)
                m.neibours.append(self)
        mlist.append(self)
        return

    def eta_sb_and_trunc(self):
        """shadow blockage efficiency and truncation efficiency"""
        # k = 1000
        # sum_sb = 0
        # sum_trunc = 0
        # direct = Mirror.light_direct
        # d_absorber = absorber - self.cor
        # d_absorber = d_absorber / np.linalg.norm(d_absorber)
        # for i in range(0, k):
        #     cor = self._eta_scatter_light()
        #     if self._eta_light_trunc(direct, cor):
        #         sum_sb += 1
        #     elif self._eta_light_trunc(d_absorber, cor):
        #         sum_trunc += 1
        # eta_sb = 1 - sum_sb / k
        # eta_trunc = 1 - sum_trunc / (k - sum_sb)
        # return (eta_sb, eta_trunc)
        return (1, 1)

    def _eta_scatter_light(self):
        v1 = np.array([self.norm[1], -self.norm[0], 0])
        v1 = v1 / np.linalg.norm(v1)
        v2 = np.cross(v1, self.norm)
        x1 = random.random() * self.width
        x2 = random.random() * self.length
        return self.cor + x1 * v1 + x2 * v2

    def _eta_light_hit(self, direct, cor):
        v1 = np.array([self.norm[1], -self.norm[0], 0])
        v1 = v1 / np.linalg.norm(v1)
        v2 = np.cross(v1, self.norm)
        A = np.array([v1, v2, direct])
        [x1, x2, t] = np.linalg.solve(A, cor - self,cor)
        t = -t
        if (math.abs(x1) > self.width / 2) or (math.abs(x2) > self.length / 2) or (t < 0):
            return False
        else:
            return True

    def _eta_light_trunc(self, direct, cor):
        for m in self.neibours:
            if m._eta_light_hit(direct, cor):
                return True
        return False

    def eta(self):
        eta_sb, eta_trunc = self.eta_sb_and_trunc()
        eta_cos = self.eta_cos()
        eta_at = self.eta_at()
        eta_ref = self.eta_ref
        return eta_sb * eta_trunc * eta_cos * eta_at * eta_ref

    def E_mirror(self):
        return self.eta() * self.light_DNI

class Sunlight:

    def __init__(self):
        self.month = 1
        self.hour = 0

    def __iter__(self):
        self.month = 1
        self.hour = 7.5
        self.flush()
        return self

    def __next__(self):
        self.hour += 1.5
        if self.hour > 12:
            self.hour = 9
            self.month += 1
            if self.month > 12:
                raise StopIteration
        self.flush()
        return self

    def flush(self):
        alpha_s = angle_alpha_s(self.month, self.hour)
        gamma_s = angle_gamma_s(self.month, self.hour)
        z = math.sin(alpha_s)
        xy = math.cos(alpha_s)
        x = math.cos(gamma_s) * xy
        y = math.sin(gamma_s) * xy
        self.direct = np.array([x, y, z])

        H = latitude
        alpha_s = angle_alpha_s(self.month, self.hour)
        a = 0.4237 - 0.00821 * (6 - H)**2
        b = 0.5055 + 0.00595 * (6.5 - H)**2
        c = 0.2711 + 0.01858 * (2.5 - H)**2
        self.DNI = G_0 * (a + b * math.exp(- c / math.sin(alpha_s)))

def interp4d_and_mean(y0, y1, y2):
    y = np.array([y0, y1, y2])
    X = np.array([[1, 0, 0],
                  [1, 1.5**2, 1.5**4],
                  [1, 3**2, 3**4]])
    [a0, a1, a2] = np.linalg.solve(X, y)
    return (a0 * 3 + a1 * 3**3 / 3 + a2 * 3**5 / 5) / 3

def day_mean(vl1, vl2, vl3):
    res = []
    for i in range(0, len(vl1)):
        res.append(interp4d_and_mean(vl1[i], vl2[i], vl3[i]))
    return res

def year_mean(monthlist):
    res = []
    for i in range(0, len(monthlist[0])):
        sum = 0
        for j in range(0, 12):
            sum += day_list[j] * monthlist[j][i]
        res.append(sum / 365)
    return res

def mlist_mean(mlist, vlist):
    S_sum = 0
    sum = 0
    for i in range(0, len(mlist)):
        S = mlist[i].width * mlist[i].length
        S_sum += S
        sum += vlist[i] * S
    return sum / S_sum

def mlist_set_norm(mlist, sunlight):
    Mirror.light_DNI = sunlight.DNI
    Mirror.light_direct = sunlight.direct
    for m in mlist:
        m.set_norm()

def mlist_etalist(mlist):
    res = []
    for m in mlist:
        res.append(m.eta())
    return res

def mlist_etacoslist(mlist):
    res = []
    for m in mlist:
        res.append(m.eta_cos())
    return res

def mlist_etasbtrunclist(mlist):
    ressb = []
    restrunc = []
    for m in mlist:
        etasb, etatrunc = m.eta_sb_and_trunc()
        ressb.append(etasb)
        restrunc.append(etatrunc)
    return (ressb, restrunc)

def mlist_E(mlist):
    res = []
    for m in mlist:
        res.append(m.E_mirror())
    return res

def eta_mean(mlist):
    light = Sunlight()
    res_months = []
    for i in range(1, 13):
        res_hours = [[], [], []]
        light.month = i
        for j in range(0, 3):
            light.hour = 9 + 1.5 * j
            light.flush()
            mlist_set_norm(mlist, light)
            for m in mlist:
                res_hours[j].append(m.eta())
        res_months.append(day_mean(res_hours[2], res_hours[1], res_hours[0]))
    res = year_mean(res_months)
    return mlist_mean(mlist, res)

def eta_cos_mean(mlist):
    light = Sunlight()
    res_months = []
    for i in range(1, 13):
        res_hours = [[], [], []]
        light.month = i
        for j in range(0, 3):
            light.hour = 9 + 1.5 * j
            light.flush()
            mlist_set_norm(mlist, light)
            for m in mlist:
                res_hours[j].append(m.eta_cos())
        res_months.append(day_mean(res_hours[2], res_hours[1], res_hours[0]))
    res = year_mean(res_months)
    return mlist_mean(mlist, res)

def eta_sb_and_trunc_mean(mlist):
    light = Sunlight()
    res_months_sb = []
    res_months_trunc = []
    for i in range(1, 13):
        res_hours_sb = [[], [], []]
        res_hours_trunc = [[], [], []]
        light.month = i
        for j in range(0, 3):
            light.hour = 9 + 1.5 * j
            light.flush()
            mlist_set_norm(mlist, light)
            for m in mlist:
                esb, etrunc = m.eta_sb_and_trunc()
                res_hours_sb[j].append(esb)
                res_hours_trunc[j].append(etrunc)
        res_months_sb.append(day_mean(res_hours_sb[2], res_hours_sb[1], res_hours_sb[0]))
        res_months_trunc.append(day_mean(res_hours_trunc[2], res_hours_trunc[1], res_hours_trunc[0]))
    res_sb = year_mean(res_months_sb)
    res_trunc = year_mean(res_months_trunc)
    return (mlist_mean(mlist, res_sb), mlist_mean(mlist, res_trunc))

def E_mean(mlist):
    light = Sunlight()
    res_months = []
    for i in range(1, 13):
        res_hours = [[], [], []]
        light.month = i
        for j in range(0, 3):
            light.hour = 9 + 1.5 * j
            light.flush()
            mlist_set_norm(mlist, light)
            for m in mlist:
                res_hours[j].append(m.E_mirror())
        res_months.append(day_mean(res_hours[2], res_hours[1], res_hours[0]))
    res = year_mean(res_months)
    return mlist_mean(mlist, res)
