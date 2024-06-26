from datetime import datetime

from sqlalchemy import (
    Integer, String, TIMESTAMP, Boolean, BINARY, DECIMAL, ForeignKey, Date, DATE, select, func, and_
)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, Mapped, mapped_column

from common.models import EBMSBase as Base
from settings import FILTERING_DATA_STARTING_YEAR, LIST_EXCLUDED_PROD_TYPES


class Arinv(Base):
    arinv_guid: Mapped[str] = mapped_column("ARINV_GUID", primary_key=True)
    recno5: Mapped[int] = mapped_column("RECNO5")
    id: Mapped[str] = mapped_column("ID")
    name: Mapped[str] = mapped_column("NAME")
    address1: Mapped[str] = mapped_column("ADDRESS1")
    address2: Mapped[str] = mapped_column("ADDRESS2")
    city: Mapped[str] = mapped_column("CITY")
    state: Mapped[str] = mapped_column("STATE")
    # zip: Mapped[str] = mapped_column("ZIP")
    invoice: Mapped[str] = mapped_column("INVOICE")
    descr: Mapped[str] = mapped_column("DESCR")
    inv_date: Mapped[datetime] = mapped_column("INV_DATE")
    due_date: Mapped[datetime] = mapped_column("DUE_DATE")
    dis_date: Mapped[datetime] = mapped_column("DIS_DATE")
    # iddiscount: Mapped[str] = mapped_column("IDDISCOUNT")
    # idcharge: Mapped[str] = mapped_column("IDCHARGE")
    discount: Mapped[str] = mapped_column("DISCOUNT")
    # charge: Mapped[str] = mapped_column("CHARGE")
    # terms: Mapped[str] = mapped_column("TERMS")
    # in_level: Mapped[str] = mapped_column("IN_LEVEL")
    po_no: Mapped[str] = mapped_column("PO_NO")
    # salesman: Mapped[str] = mapped_column("SALESMAN")
    ship_via: Mapped[str] = mapped_column("SHIP_VIA")
    e_date: Mapped[datetime] = mapped_column("E_DATE")
    overdue: Mapped[float] = mapped_column("OVERDUE")
    # freight: Mapped[int] = mapped_column("FREIGHT")
    tax: Mapped[float] = mapped_column("TAX")
    subtotal: Mapped[float] = mapped_column("SUBTOTAL")
    total: Mapped[float] = mapped_column("TOTAL")
    status: Mapped[str] = mapped_column("STATUS")
    total_paid: Mapped[float] = mapped_column("TOTAL_PAID")
    # total_w: Mapped[float] = mapped_column("TOTAL_W")
    # balance: Mapped[float] = mapped_column("BALANCE")
    # check_no: Mapped[str] = mapped_column("CHECK_NO")
    # check_date: Mapped[datetime] = mapped_column("CHECK_DATE")
    # c_id: Mapped[str] = mapped_column("C_ID")
    c_name: Mapped[str] = mapped_column("C_NAME")
    c_address1: Mapped[str] = mapped_column("C_ADDRESS1")
    c_address2: Mapped[str] = mapped_column("C_ADDRESS2")
    c_city: Mapped[str] = mapped_column("C_CITY")
    c_state: Mapped[str] = mapped_column("C_STATE")
    # c_zip: Mapped[str] = mapped_column("C_ZIP")
    email: Mapped[str] = mapped_column("EMAIL")
    billing_co: Mapped[str] = mapped_column("BILLING_CO")
    ship_date: Mapped[datetime] = mapped_column("SHIP_DATE")
    frght_amt: Mapped[str] = mapped_column("FRGHT_AMT")
    frght_type: Mapped[str] = mapped_column("FRGHT_TYPE", String)
    user_name: Mapped[str] = mapped_column("USER_NAME", String)
    # was_proc: Mapped[bool] = mapped_column("WAS_PROC", Boolean)
    # memo: Mapped[str] = mapped_column("MEMO", String)
    # signature: Mapped[bool] = mapped_column("SIGNATURE", BINARY)
    # country: Mapped[str] = mapped_column("COUNTRY", String)
    # c_country: Mapped[str] = mapped_column("C_COUNTRY", String)
    # close_date: Mapped[datetime] = mapped_column("CLOSE_DATE", TIMESTAMP)
    # so_tax: Mapped[float] = mapped_column("SO_TAX", DECIMAL)
    # man_tax: Mapped[bool] = mapped_column("MAN_TAX", Boolean)
    orig_inv: Mapped[str] = mapped_column("ORIG_INV", String)
    orig_aid: Mapped[str] = mapped_column("ORIG_AID", String)
    # print_time: Mapped[str] = mapped_column("PRINT_TIME", String)
    # c_fr_order: Mapped[str] = mapped_column("C_FR_ORDER", Boolean)
    crea_date: Mapped[datetime] = mapped_column("CREA_DATE", TIMESTAMP)
    crea_time: Mapped[str] = mapped_column("CREA_TIME", String)
    # proc_date: Mapped[datetime] = mapped_column("PROC_DATE", TIMESTAMP)
    # proc_time: Mapped[str] = mapped_column("PROC_TIME", String)
    # ar_trade: Mapped[str] = mapped_column("AR_TRADE", String)
    # freight_gl: Mapped[str] = mapped_column("FREIGHT_GL", String)
    # finance: Mapped[str] = mapped_column("FINANCE", String)
    # cust_disc: Mapped[str] = mapped_column("CUST_DISC", String)
    # down_pay: Mapped[str] = mapped_column("DOWN_PAY", String)
    # def_dept: Mapped[str] = mapped_column("DEF_DEPT", String)
    # warehouse: Mapped[str] = mapped_column("WAREHOUSE", String)
    autoid: Mapped[str] = mapped_column("AUTOID", String)
    csend_date: Mapped[datetime] = mapped_column("CSEND_DATE", TIMESTAMP)
    csend_time: Mapped[str] = mapped_column("CSEND_TIME", String)
    csend_mes: Mapped[str] = mapped_column("CSEND_MES", String)
    c_rate: Mapped[str] = mapped_column("C_RATE", String)
    curr_id: Mapped[str] = mapped_column("CURR_ID", String)
    copied: Mapped[bool] = mapped_column("COPIED", Boolean)
    prevord: Mapped[str] = mapped_column("PREVORD", String)
    # trim: Mapped[bool] = mapped_column("TRIM", Boolean)
    # metal: Mapped[bool] = mapped_column("METAL", Boolean)
    # div_aid: Mapped[str] = mapped_column("DIV_AID", String)
    # authorized: Mapped[float] = mapped_column("AUTHORIZED", DECIMAL)
    # web_sale:  Mapped[bool] = mapped_column("WEB_SALE", Boolean)
    # phone: Mapped[str] = mapped_column("PHONE", String)
    # web_aid: Mapped[str] = mapped_column("WEB_AID", String)
    # cf_email: Mapped[str] = mapped_column("CF_EMAIL", String)
    # cf_sent: Mapped[bool] = mapped_column("CF_SENT", Boolean)
    # rollexdt: Mapped[datetime] = mapped_column("ROLLEXDT", TIMESTAMP)
    # rollprocdt: Mapped[datetime] = mapped_column("ROLLPROCDT", TIMESTAMP)
    # c_email: Mapped[str] = mapped_column("C_EMAIL", String)
    # c_phone: Mapped[str] = mapped_column("C_PHONE", String)
    # last_print: Mapped[str] = mapped_column("LAST_PRINT", String)
    # handling: Mapped[float] = mapped_column("HANDLING", DECIMAL)
    # freightexp: Mapped[str] = mapped_column("FREIGHTEXP", String)
    # ly_pts_got: Mapped[float] = mapped_column("LY_PTS_GOT", DECIMAL)
    # to_b_sent: Mapped[bool] = mapped_column("TO_B_SENT", Boolean)
    # internalnt: Mapped[str] = mapped_column("INTERNALNT", String)
    # out_city: Mapped[bool] = mapped_column("OUT_CITY", Boolean)
    # c_tax: Mapped[float] = mapped_column("C_TAX", DECIMAL)
    # c_manual: Mapped[bool] = mapped_column("C_MANUAL", Boolean)
    # arpw_id: Mapped[str] = mapped_column("ARPW_ID", String)
    # comis_paid: Mapped[bool] = mapped_column("COMIS_PAID", Boolean)
    # job_id: Mapped[str] = mapped_column("JOB_ID", String)
    # num_bill: Mapped[str] = mapped_column("NUM_BILL", String)
    # use_jobret: Mapped[bool] = mapped_column("USE_JOBRET", Boolean)
    # from_tandm: Mapped[bool] = mapped_column("FROM_TANDM", Boolean)
    # subilnoret: Mapped[float] = mapped_column("SUBILNORET", DECIMAL)
    # arqtaidsrc: Mapped[str] = mapped_column("ARQTAIDSRC", String)
    # usetaxed: Mapped[bool] = mapped_column("USETAXED", Boolean)
    # cntct_aid: Mapped[str] = mapped_column("CNTCT_AID", String)
    # ccntct_aid: Mapped[str] = mapped_column("CCNTCT_AID", String)
    # man_usetax: Mapped[bool] = mapped_column("MAN_USETAX", Boolean)
    # externalid: Mapped[str] = mapped_column("EXTERNALID", String) # included in test mirror db
    # p_rounddif: Mapped[float] = mapped_column("P_ROUNDDIF", DECIMAL) # included in test mirror db
    details = relationship('Arinvdet', back_populates="order", innerjoin=True, order_by='Arinvdet.autoid', primaryjoin="""and_(Arinv.autoid == Arinvdet.doc_aid, Arinv.autoid == Arinvdet.doc_aid, Arinvdet.category != '', Arinvdet.category != 'Vents', Arinvdet.par_time == '', Arinvdet.inven != None, Arinvdet.inven != '')""")
    _sales_order = None
    _count_items = None
    _details_data = None

    @hybrid_property
    def count_items(self):
        return self._count_items

    @count_items.expression
    def count_items(self):
        return select(
            func.count(Arinvdet.doc_aid).label('count_items')
        ).where(
            Arinvdet.doc_aid == self.autoid,
            Arinvdet.inv_date >= FILTERING_DATA_STARTING_YEAR,
            # Arinvdet.category != None,
            Arinvdet.category != '',
            Arinvdet.category != 'Vents',
            # Inventry.prod_type.notin_(LIST_EXCLUDED_PROD_TYPES),
            Arinvdet.par_time == '',
            Arinvdet.inven != None,
            Arinvdet.inven != '',
        ).correlate_except(
            Arinvdet
        ).scalar_subquery()

    @count_items.setter
    def count_items(self, value):
        self._count_items = value

    @hybrid_property
    def sales_order(self):
        return self._sales_order

    @sales_order.setter
    def sales_order(self, value):
        self._sales_order = value

    @property
    def details_data(self):
        return self._details_data

    # @details.setter
    # def details_data(self, value):
    #     self._details = value

    # @details.expression
    # def details(self):
    #     return select(Arinvdet).where(
    #         and_(Arinvdet.doc_aid == self.autoid, Arinvdet.inv_date >= FILTERING_DATA_STARTING_YEAR,
    #              # Arinvdet.category != None,
    #              Arinvdet.category != '',
    #              Arinvdet.category != 'Vents',
    #              # Inventry.prod_type.notin_(LIST_EXCLUDED_PROD_TYPES),
    #              Arinvdet.par_time == '',
    #              Arinvdet.inven != None,
    #              Arinvdet.inven != '',
    #              )
    #     ).correlate_except(
    #         Arinvdet
    #     )
    @details_data.setter
    def details_data(self, value):
        self._details_data = value


class Arinvdet(Base):
    arinvdet_guid: Mapped[str] = mapped_column('ARINVDET_GUID', String, primary_key=True)
    recno5: Mapped[int] = mapped_column('RECNO5', Integer)
    invoice: Mapped[str] = mapped_column('INVOICE', String)
    id: Mapped[str] = mapped_column('ID', String)
    # doc_type: Mapped[str] = mapped_column('DOC_TYPE', String)
    doc_aid: Mapped[str] = mapped_column('DOC_AID', String, ForeignKey('ARINV.AUTOID'))
    inv_date: Mapped[datetime] = mapped_column('INV_DATE', TIMESTAMP)
    quan: Mapped[float] = mapped_column('QUAN', DECIMAL)
    # ship: Mapped[float] = mapped_column('SHIP', DECIMAL)
    # m_quan: Mapped[float] = mapped_column('M_QUAN', DECIMAL)
    # orig_quan: Mapped[float] = mapped_column('ORIG_QUAN', DECIMAL)
    inven: Mapped[str] = mapped_column('INVEN', String, ForeignKey('INVENTRY.ID'))
    c_type: Mapped[float] = mapped_column('C_TYPE', DECIMAL)
    # unit_meas: Mapped[str] = mapped_column('UNIT_MEAS', String)
    descr: Mapped[str] = mapped_column('DESCR', String)
    # unit: Mapped[float] = mapped_column('UNIT', DECIMAL)
    # price: Mapped[float] = mapped_column('PRICE', DECIMAL)
    # so_amount: Mapped[float] = mapped_column('SO_AMOUNT', DECIMAL)
    discount: Mapped[float] = mapped_column('DISCOUNT', DECIMAL)
    sodiscount: Mapped[float] = mapped_column('SODISCOUNT', DECIMAL)
    # timestamp: Mapped[str] = mapped_column('TIMESTAMP', String)
    par_time: Mapped[str] = mapped_column('PAR_TIME', String)
    # gpar_time: Mapped[str] = mapped_column('GPAR_TIME', String)
    status: Mapped[float] = mapped_column('STATUS', DECIMAL)
    # u_cost: Mapped[float] = mapped_column('U_COST', DECIMAL)
    # costs: Mapped[float] = mapped_column('COSTS', DECIMAL)
    # tax_group: Mapped[str] = mapped_column('TAX_GROUP', String)
    # exm_overid: Mapped[str] = mapped_column('EXM_OVERID', String)
    ship_date: Mapped[DATE] = mapped_column('SHIP_DATE', Date)
    weight: Mapped[float] = mapped_column('WEIGHT', DECIMAL)
    # print: Mapped[bool] = mapped_column('PRINT', Boolean)
    # ap_partime: Mapped[str] = mapped_column('AP_PARTIME', String)
    # print_quan: Mapped[bool] = mapped_column('PRINT_QUAN', Boolean)
    # print_uom: Mapped[bool] = mapped_column('PRINT_UOM', Boolean)
    # account: Mapped[str] = mapped_column('ACCOUNT', String)
    # warehouse: Mapped[str] = mapped_column('WAREHOUSE', String)
    autoid: Mapped[str] = mapped_column('AUTOID', String)
    # pcm_type: Mapped[float] = mapped_column('PCM_TYPE', DECIMAL)
    # pcm_perc: Mapped[float] = mapped_column('PCM_PERC', DECIMAL)
    # mto: Mapped[bool] = mapped_column('MTO', Boolean)
    # mto_d_sync: Mapped[bool] = mapped_column('MTO_D_SYNC', Boolean)
    # drop_ven: Mapped[str] = mapped_column('DROP_VEN', String)
    # drop_part: Mapped[str] = mapped_column('DROP_PART', String)
    # drop_aid: Mapped[str] = mapped_column('DROP_AID', String)
    # purc_meth: Mapped[float] = mapped_column('PURC_METH', DECIMAL)
    # c_price: Mapped[float] = mapped_column('C_PRICE', DECIMAL)
    # c_unit: Mapped[float] = mapped_column('C_UNIT', DECIMAL)
    # fxline: Mapped[bool] = mapped_column('FXLINE', Boolean)
    # c_formula: Mapped[str] = mapped_column('C_FORMULA', String)
    width: Mapped[str] = mapped_column('WIDTH', String)
    widthd: Mapped[float] = mapped_column('WIDTHD', DECIMAL)
    height: Mapped[str] = mapped_column('HEIGHT', String)
    heightd: Mapped[float] = mapped_column('HEIGHTD', DECIMAL)
    # dem: Mapped[str] = mapped_column('DEM', String)
    demd: Mapped[float] = mapped_column('DEMD', DECIMAL)
    # manual_p: Mapped[bool] = mapped_column('MANUAL_P', Boolean)
    # manual_c: Mapped[bool] = mapped_column('MANUAL_C', Boolean)
    # round: Mapped[float] = mapped_column('ROUND', DECIMAL)
    # comment: Mapped[str] = mapped_column('COMMENT', String)
    # ea_quan: Mapped[float] = mapped_column('EA_QUAN', DECIMAL)
    # r_ea_quan: Mapped[float] = mapped_column('R_EA_QUAN', DECIMAL)
    # report_n: Mapped[str] = mapped_column('REPORT_N', String)
    # random_w: Mapped[bool] = mapped_column('RANDOM_W', Boolean)
    # random_h: Mapped[bool] = mapped_column('RANDOM_H', Boolean)
    # item_num: Mapped[str] = mapped_column('ITEM_NUM', String)
    # feet: Mapped[float] = mapped_column('FEET', DECIMAL)
    # inchesd: Mapped[float] = mapped_column('INCHESD', DECIMAL)
    # inches: Mapped[str] = mapped_column('INCHES', String)
    # c_mfg: Mapped[float] = mapped_column('C_MFG', DECIMAL)
    # r_serial: Mapped[str] = mapped_column('R_SERIAL', String)
    # su_autoid: Mapped[str] = mapped_column('SU_AUTOID', String)
    # trade_in: Mapped[bool] = mapped_column('TRADE_IN', Boolean)
    # in_level: Mapped[str] = mapped_column('IN_LEVEL', String)
    # job_id: Mapped[str] = mapped_column('JOB_ID', String)
    # jobstg_id: Mapped[str] = mapped_column('JOBSTG_ID', String)
    # aia: Mapped[str] = mapped_column('AIA', String)
    # retn_type: Mapped[str] = mapped_column('RETN_TYPE', String)
    # retn_perc: Mapped[float] = mapped_column('RETN_PERC', DECIMAL)
    # int_note: Mapped[str] = mapped_column('INT_NOTE', String)
    # tax_expl: Mapped[str] = mapped_column('TAX_EXPL', String)
    # on_site: Mapped[float] = mapped_column('ON_SITE', DECIMAL)
    order = relationship('Arinv', back_populates='details', primaryjoin="Arinv.autoid == Arinvdet.doc_aid")
    rel_inventry = relationship('Inventry', back_populates='arinvdet', primaryjoin="Inventry.id == Arinvdet.inven", lazy='selectin')
    _item = None
    _customer = None
    _category = None
    _profile = None
    _color = None
    _order_status = None

    @hybrid_property
    def category(self):
        return self._category

    @category.expression
    def category(cls):
        return select(Inventry.prod_type).where(Inventry.id == Arinvdet.inven).correlate_except(Inventry).scalar_subquery().label('category')

    @category.setter
    def category(self, value):
        self._category = value

    @hybrid_property
    def profile(self):
        return self._profile

    @profile.expression
    def profile(cls):
        return select(Inventry.rol_profil).where(Inventry.id == Arinvdet.inven).correlate_except(Inventry).scalar_subquery().label('profile')

    @profile.setter
    def profile(self, value):
        self._profile = value

    @hybrid_property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        self._color = value

    @color.expression
    def color(cls):
        return select(Inventry.rol_color).where(Inventry.id == Arinvdet.inven).correlate_except(Inventry).scalar_subquery().label('color')

    @hybrid_property
    def customer(self):
        return self._customer

    @customer.expression
    def customer(cls):
        return select(Arinv.name).where(Arinv.autoid == Arinvdet.doc_aid).correlate_except(Arinv).scalar_subquery().label('customer')

    @customer.setter
    def customer(self, value):
        self._customer = value

    @hybrid_property
    def order_status(self):
        return self._order_status

    @order_status.expression
    def order_status(cls):
        return select(Arinv.status).where(Arinv.autoid == Arinvdet.doc_aid).correlate_except(Arinv).scalar_subquery().label('order_status')

    @order_status.setter
    def order_status(self, value):
        self._order_status = value

    @hybrid_property
    def item(self):
        return self._item

    @item.setter
    def item(self, value):
        self._item = value
    #
    # @hybrid_property
    # def invoice(self):
    #     return str(self.order.invoice).strip()


class Inprodtype(Base):
    inprodtype_guid: Mapped[str] = mapped_column('INPRODTYPE_GUID', String(36), primary_key=True)
    recno5: Mapped[int] = mapped_column('RECNO5', Integer)
    prod_type: Mapped[str] = mapped_column('PROD_TYPE', String(20))
    ar_aid: Mapped[str] = mapped_column('AR_AID', String(16))
    autoid: Mapped[str] = mapped_column('AUTOID', String(16))
    inventries = relationship(
        'Inventry', back_populates='inprodtype', innerjoin=True, primaryjoin="Inprodtype.prod_type == Inventry.prod_type"
    )


class Inventry(Base):
    inventry_guid: Mapped[str] = mapped_column('INVENTRY_GUID', String, primary_key=True)
    recno5: Mapped[int] = mapped_column('RECNO5', Integer)
    id: Mapped[str] = mapped_column('ID', String)
    # tree_id: Mapped[str] = mapped_column('TREE_ID', String)
    # upc: Mapped[str] = mapped_column('UPC', String)
    # type: #Mapped[str] = mapped_column('TYPE', String)
    # c_type: Mapped[DECIMAL] = mapped_column('C_TYPE', DECIMAL)
    # descr_1: Mapped[str] = mapped_column('DESCR_1', String)
    # descr_1prn: Mapped[bool] = mapped_column('DESCR_1PRN', Boolean)
    # descr_1prp: Mapped[bool] = mapped_column('DESCR_1PRP', Boolean)
    # descr_2: Mapped[str] = mapped_column('DESCR_2', String)
    # descr_2prn: Mapped[bool] = mapped_column('DESCR_2PRN', Boolean)
    # descr_2prp: Mapped[bool] = mapped_column('DESCR_2PRP', Boolean)
    # descr_3: Mapped[str] = mapped_column('DESCR_3', String)
    # descr_3prn: Mapped[bool] = mapped_column('DESCR_3PRN', Boolean)
    # descr_3prp: Mapped[bool] = mapped_column('DESCR_3PRP', Boolean)
    # markup: Mapped[str] = mapped_column('MARKUP', String)
    # markup_id: Mapped[str] = mapped_column('MARKUP_ID', String)
    # base: Mapped[DECIMAL] = mapped_column('BASE', DECIMAL)
    # cost: Mapped[DECIMAL] = mapped_column('COST', DECIMAL)
    # tax_group: Mapped[str] = mapped_column('TAX_GROUP', String)
    # weight: Mapped[DECIMAL] = mapped_column('WEIGHT', DECIMAL)
    # date: Mapped[Date] = mapped_column('DATE', Date)
    # quan2order: Mapped[DECIMAL] = mapped_column('QUAN2ORDER', DECIMAL)
    # count: Mapped[DECIMAL] = mapped_column('COUNT', DECIMAL)
    # location: Mapped[str] = mapped_column('LOCATION', String)
    # min_inven: Mapped[DECIMAL] = mapped_column('MIN_INVEN', DECIMAL)
    # max_inven: Mapped[DECIMAL] = mapped_column('MAX_INVEN', DECIMAL)
    # order_amt: Mapped[DECIMAL] = mapped_column('ORDER_AMT', DECIMAL)
    # pri_vendor: Mapped[str] = mapped_column('PRI_VENDOR', String)
    # pur_o: Mapped[DECIMAL] = mapped_column('PUR_O', DECIMAL)
    # pur_s: Mapped[DECIMAL] = mapped_column('PUR_S', DECIMAL)
    # sales_o: Mapped[DECIMAL] = mapped_column('SALES_O', DECIMAL)
    # sales_s: Mapped[DECIMAL] = mapped_column('SALES_S', DECIMAL)
    # m_in_o: Mapped[DECIMAL] = mapped_column('M_IN_O', DECIMAL)
    # m_in_s: Mapped[DECIMAL] = mapped_column('M_IN_S', DECIMAL)
    # m_out_o: Mapped[DECIMAL] = mapped_column('M_OUT_O', DECIMAL)
    # m_out_s: Mapped[DECIMAL] = mapped_column('M_OUT_S', DECIMAL)
    # job_out_o: Mapped[DECIMAL] = mapped_column('JOB_OUT_O', DECIMAL)
    # job_out_s: Mapped[DECIMAL] = mapped_column('JOB_OUT_S', DECIMAL)
    # each_unit: Mapped[str] = mapped_column('EACH_UNIT', String)
    # int_quan: Mapped[bool] = mapped_column('INT_QUAN', Boolean)
    # def_unit: Mapped[str] = mapped_column('DEF_UNIT', String)
    # last_chk_u: Mapped[str] = mapped_column('LAST_CHK_U', String)
    # last_chk_d: Mapped[Date] = mapped_column('LAST_CHK_D', Date)
    # last_chk_t: Mapped[str] = mapped_column('LAST_CHK_T', String)
    # auto_cost: Mapped[bool] = mapped_column('AUTO_COST', Boolean)
    # memo: Mapped[str] = mapped_column('MEMO', String)
    # mfg: Mapped[str] = mapped_column('MFG', String)
    # mfg_part: Mapped[str] = mapped_column('MFG_PART', String)
    # web: Mapped[str] = mapped_column('WEB', String)
    # est_hours: Mapped[DECIMAL] = mapped_column('EST_HOURS', DECIMAL)
    # def_work: Mapped[str] = mapped_column('DEF_WORK', String)
    # perc_adj: Mapped[DECIMAL] = mapped_column('PERC_ADJ', DECIMAL)
    # perc_adj_c: Mapped[DECIMAL] = mapped_column('PERC_ADJ_C', DECIMAL)
    # pur_memo: Mapped[str] = mapped_column('PUR_MEMO', String)
    # sale_class: Mapped[str] = mapped_column('SALE_CLASS', String)
    # updatecost: Mapped[bool] = mapped_column('UPDATECOST', Boolean)
    # updvencost: Mapped[bool] = mapped_column('UPDVENCOST', Boolean)
    # ins_acc: Mapped[DECIMAL] = mapped_column('INS_ACC', DECIMAL)
    # returndays: Mapped[str] = mapped_column('RETURNDAYS', String)
    # sale_acc: Mapped[str] = mapped_column('SALE_ACC', String)
    # use_pl_gl: Mapped[bool] = mapped_column('USE_PL_GL', Boolean)
    # pur_acc: Mapped[str] = mapped_column('PUR_ACC', String)
    # adjust: Mapped[str] = mapped_column('ADJUST', String)
    # asset: Mapped[str] = mapped_column('ASSET', String)
    # use_itemgl: Mapped[bool] = mapped_column('USE_ITEMGL', Boolean)
    # mfg_cost: Mapped[str] = mapped_column('MFG_COST', String)
    autoid: Mapped[str] = mapped_column('AUTOID', String)
    # fixed_cost: Mapped[bool] = mapped_column('FIXED_COST', Boolean)
    # adj_inven: Mapped[str] = mapped_column('ADJ_INVEN', String)
    # autoserial: Mapped[bool] = mapped_column('AUTOSERIAL', Boolean)
    # weigh_it: Mapped[bool] = mapped_column('WEIGH_IT', Boolean)
    # def_type: Mapped[str] = mapped_column('DEF_TYPE', String)
    # ent_task: Mapped[bool] = mapped_column('ENT_TASK', Boolean)
    # purc_meth: Mapped[DECIMAL] = mapped_column('PURC_METH', DECIMAL)
    # pur_ssed: Mapped[bool] = mapped_column('PUR_SSED', Boolean)
    # s_cust_i: Mapped[str] = mapped_column('S_CUST_I', String)
    # d_width: Mapped[DECIMAL] = mapped_column('D_WIDTH', DECIMAL)
    # d_height: Mapped[DECIMAL] = mapped_column('D_HEIGHT', DECIMAL)
    # d_dem: Mapped[DECIMAL] = mapped_column('D_DEM', DECIMAL)
    # width: Mapped[DECIMAL] = mapped_column('WIDTH', DECIMAL)
    # width_r: Mapped[bool] = mapped_column('WIDTH_R', Boolean)
    # height: Mapped[DECIMAL] = mapped_column('HEIGHT', DECIMAL)
    # height_r: Mapped[bool] = mapped_column('HEIGHT_R', Boolean)
    # dem: Mapped[DECIMAL] = mapped_column('DEM', DECIMAL)
    # dem_r: Mapped[bool] = mapped_column('DEM_R', Boolean)
    # waste_p: Mapped[DECIMAL] = mapped_column('WASTE_P', DECIMAL)
    # item_num: Mapped[bool] = mapped_column('ITEM_NUM', Boolean)
    # d_replace: Mapped[bool] = mapped_column('D_REPLACE', Boolean)
    # trade_in: Mapped[bool] = mapped_column('TRADE_IN', Boolean)
    # trade_acc: Mapped[str] = mapped_column('TRADE_ACC', String)
    # su_autoid: Mapped[str] = mapped_column('SU_AUTOID', String)
    # show_stock: Mapped[str] = mapped_column('SHOW_STOCK', String)
    # ostk_msg: Mapped[str] = mapped_column('OSTK_MSG', String)
    # hide_wwprc: Mapped[bool] = mapped_column('HIDE_WWPRC', Boolean)
    # web_descr1: Mapped[str] = mapped_column('WEB_DESCR1', String)
    # web_descr2: Mapped[str] = mapped_column('WEB_DESCR2', String)
    # web_descr3: Mapped[str] = mapped_column('WEB_DESCR3', String)
    # comp_tpl: Mapped[str] = mapped_column('COMP_TPL', String)
    # comp_descr: Mapped[str] = mapped_column('COMP_DESCR', String)
    # template: Mapped[str] = mapped_column('TEMPLATE', String)
    # descr1copy: Mapped[bool] = mapped_column('DESCR1COPY', Boolean)
    # descr2copy: Mapped[bool] = mapped_column('DESCR2COPY', Boolean)
    # descr3copy: Mapped[bool] = mapped_column('DESCR3COPY', Boolean)
    # seasonal: Mapped[str] = mapped_column('SEASONAL', String)
    # show_web: Mapped[bool] = mapped_column('SHOW_WEB', Boolean)
    # acc_label: Mapped[str] = mapped_column('ACC_LABEL', String)
    # showserial: Mapped[bool] = mapped_column('SHOWSERIAL', Boolean)
    # perc_adj_n: Mapped[DECIMAL] = mapped_column('PERC_ADJ_N', DECIMAL)
    # rol_fnprod: Mapped[bool] = mapped_column('ROL_FNPROD', Boolean)
    # rol_rwmtrl: Mapped[bool] = mapped_column('ROL_RWMTRL', Boolean)
    # rol_gauge: Mapped[DECIMAL] = mapped_column('ROL_GAUGE', DECIMAL)
    # rol_thick: Mapped[DECIMAL] = mapped_column('ROL_THICK', DECIMAL)
    rol_color: Mapped[str] = mapped_column('ROL_COLOR', String)
    # rol_dense: Mapped[DECIMAL] = mapped_column('ROL_DENSE', DECIMAL)
    # rol_width: Mapped[DECIMAL] = mapped_column('ROL_WIDTH', DECIMAL)
    # rol_fnexdt: Mapped[Date] = mapped_column('ROL_FNEXDT', Date)
    # rol_rwexdt: Mapped[Date] = mapped_column('ROL_RWEXDT', Date)
    # lotselopt: Mapped[str] = mapped_column('LOTSELOPT', String)
    # show_lots: Mapped[bool] = mapped_column('SHOW_LOTS', Boolean)
    # inactive: Mapped[bool] = mapped_column('INACTIVE', Boolean)
    # notqtysell: Mapped[bool] = mapped_column('NOTQTYSELL', Boolean)
    # no_search: Mapped[bool] = mapped_column('NO_SEARCH', Boolean)
    rol_profil: Mapped[str] = mapped_column('ROL_PROFIL', String)
    # value: Mapped[DECIMAL] = mapped_column('VALUE', DECIMAL)
    # comp_flatv: Mapped[bool] = mapped_column('COMP_FLATV', Boolean)
    # jobstg_id: Mapped[str] = mapped_column('JOBSTG_ID', String)
    # cto_prompt: Mapped[DECIMAL] = mapped_column('CTO_PROMPT', DECIMAL)
    # tree_path: Mapped[str] = mapped_column('TREE_PATH', String)
    # int_note: Mapped[str] = mapped_column('INT_NOTE', String)
    # upc2: Mapped[str] = mapped_column('UPC2', String)
    # upc3: Mapped[str] = mapped_column('UPC3', String)
    # def_to_ser: Mapped[bool] = mapped_column('DEF_TO_SER', Boolean)
    # def_to_pri: Mapped[bool] = mapped_column('DEF_TO_PRI', Boolean)
    # usetaxelig: Mapped[bool] = mapped_column('USETAXELIG', Boolean)
    # usetax_acc: Mapped[str] = mapped_column('USETAX_ACC', String)
    # externalid: Mapped[str] = mapped_column('EXTERNALID', String)
    # jc_offset: Mapped[bool] = mapped_column('JC_OFFSET', Boolean)
    # isshortcut: Mapped[bool] = mapped_column('ISSHORTCUT', Boolean)
    # av_in_off: Mapped[DECIMAL] = mapped_column('AV_IN_OFF', DECIMAL)
    # av_out_off: Mapped[DECIMAL] = mapped_column('AV_OUT_OFF', DECIMAL)
    # oh_in_off: Mapped[DECIMAL] = mapped_column('OH_IN_OFF', DECIMAL)
    # oh_out_off: Mapped[DECIMAL] = mapped_column('OH_OUT_OFF', DECIMAL)
    # no_in_off: Mapped[DECIMAL] = mapped_column('NO_IN_OFF', DECIMAL)
    # no_out_off: Mapped[DECIMAL] = mapped_column('NO_OUT_OFF', DECIMAL)
    prod_type: Mapped[str] = mapped_column("PROD_TYPE", String, ForeignKey('INPRODTYPE.PROD_TYPE'))
    arinvdet = relationship("Arinvdet", back_populates="rel_inventry", uselist=False)
    inprodtype = relationship("Inprodtype", back_populates="inventries", primaryjoin='Inventry.prod_type == Inprodtype.prod_type')

