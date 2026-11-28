"""Generated data for cenit. Regenerate with scripts/generate_data.py."""

from __future__ import annotations

from datetime import date
from types import MappingProxyType
from typing import Mapping

from cenit._types import (
    AccountNumberLengthScope,
    AccountNumberLengthVariant,
    AccountTypesAndLengths,
    EntityType,
    EntityTypeTotals,
    Participant,
    Totals,
    normalize_name,
)

SCHEMA_VERSION = 2
VERSION = '0.1.0'
SOURCE_DATE = date(2026, 11, 27)
SOURCE_SHA256 = 'b4066b93294e7c36fa0f9e35ef5b8da007eb718b34168f24cb701939a45804d6'
SOURCE_URL = 'https://www.banrep.gov.co/sites/default/files/codigos-compensacion-cenit.pdf'
SOURCE_FETCHED_AT = '2026-11-27T22:44:53.264423+00:00'

FOOTNOTES: Mapping[str, str] = MappingProxyType(
{
    '(*)': 'Linked before May 2025',
    '(**)': 'Used for special collection agreements',
    '(***)': 'Includes leading zeros',
    '(****)': 'Electronic deposit service available but not enabled in CENIT',
}
)

CSV_LINES: Mapping[str, str] = MappingProxyType(
{
    '1084': 'APORTES EN LÍNEA S.A.,1084,(*),,,,,,X,,SI,N/A,N/A,N/A,',
    '1086': 'ASOPAGOS,1086,(*),,,,,,X,,SI,N/A,N/A,N/A,',
    '1899': 'AVAL SOLUCIONES DIGITALES - DALE,1899,3/07/2025,,,,,,,X,SI,N/A,N/A,12,DALE',
    '1058': 'BAN100 S.A.,1058,(*),X,,,,,X,,SI,13,13,N/A,',
    '1059': 'BANCAMÍA,1059,(*),X,,,,,,,NO,16,N/A,(****),',
    '1040': 'BANCO AGRARIO DE COLOMBIA,1040,(*),X,,,,,X,,SI,12,12,(****),',
    '1052': 'BANCO AV VILLAS,1052,(*),X,,,,,X,,SI,9,9,9,DEPÓSITOS DIGITALES',
    '1061': 'BANCO BANCOOMEVA,1061,(*),X,,,,,X,,SI,12,12,(****),',
    '1013': 'BANCO BBVA,1013,(*),X,,,,,X,,SI,"(5, 7,13)**, 9, 10, 12, 14, 16","(5, 7)**, 9, 10, 12, 14, 16",10,DINERO MOVIL',
    '1032': 'BANCO CAJA SOCIAL,1032,(*),X,,,,,X,,SI,11 y 13,11,(****),',
    '1009': 'BANCO CITIBANK,1009,(*),X,,,,,X,,SI,10,10,N/A,',
    '1066': 'BANCO COOPCENTRAL,1066,(*),X,,,,,X,,SI,9 y 13,9 y 13,9 y 13,LETMI',
    '1051': 'BANCO DAVIVIENDA,1051,(*),X,,,,,X,,SI,16,16,10,DAVIPLATA',
    '1001': 'BANCO DE BOGOTÁ,1001,(*),X,,,,,X,,SI,9,9,N/A,',
    '1023': 'BANCO DE OCCIDENTE,1023,(*),X,,,,,X,,SI,9,9,N/A,',
    '1062': 'BANCO FALABELLA,1062,(*),X,,,,,X,,SI,12,12,N/A,',
    '1063': 'BANCO FINANDINA,1063,(*),X,,,,,,,SI,10,10,N/A,',
    '1012': 'BANCO GNB SUDAMERIS,1012,(*),X,,,,,X,,SI,18,18,N/A,',
    '1006': 'BANCO ITAÚ,1006,(*),X,,,,,X,,SI,9,9,N/A,',
    '1071': 'BANCO JP MORGAN,1071,(*),X,,,,,,,SI,N/A,10,N/A,',
    '1047': 'BANCO MUNDO MUJER,1047,(*),X,,,,,,,SI,14,N/A,N/A,',
    '1060': 'BANCO PICHINCHA,1060,(*),X,,,,,X,,NO,9,9,N/A,',
    '1002': 'BANCO POPULAR,1002,(*),X,,,,,X,,SI,12,12,N/A,',
    '1000': 'BANCO REPÚBLICA,1000,(*),X,,,,,,,NO,N/A,N/A,N/A,',
    '1065': 'BANCO SANTANDER DE NEGOCIOS,1065,(*),X,,,,,,,SI,9,9,N/A,',
    '1069': 'BANCO SERFINANZA,1069,(*),X,,,,,,,SI,12,12,12,CLICuenta',
    '1007': 'BANCOLOMBIA,1007,(*),X,,,,,X,,SI,11,11,11,Bancolombia',
    '1042': 'BNP PARIBAS,1042,(*),,,X,,,,,SI,16,N/A,N/A,',
    '1370': 'COLTEFINANCIERA,1370,(*),,,,X,,,,SI,10,N/A,N/A,',
    '1083': 'COMPENSAR,1083,(*),,,,,,X,,SI,N/A,N/A,N/A,',
    '1292': 'CONFIAR COOPERATIVA FINANCIERA,1292,(*),,X,,,,,,SI,9,N/A,N/A,',
    '1283': 'COOPERATIVA FINANCIERA DE ANTIOQUIA,1283,(*),,X,,,,,,NO,11***,N/A,10,CFA EXPRESS',
    '1289': 'COTRAFA,1289,(*),,X,,,,,,SI,13,N/A,N/A,',
    '1816': 'CREZCAMOS COMPAÑÍA DE FINANCIAMIENTO,1816,1/09/2025,,,,X,,,,NO,11,N/A,10,MOSI',
    '1019': 'DAVIBANK,1019,(*),X,,,,,X,,SI,10,10,N/A,',
    '1550': 'DECEVAL,1550,(*),,,,,X,,,NO,N/A,N/A,N/A,',
    '1683': 'DGCPTN,1683,(*),,,,,X,,,NO,N/A,N/A,N/A,',
    '1685': 'DGCPTN – REGALÍAS,1685,(*),,,,,X,,,NO,N/A,N/A,N/A,',
    '1089': 'ENLACE OPERATIVO,1089,(*),,,,,,X,,SI,N/A,N/A,N/A,',
    '1121': 'FINANCIERA JURISCOOP CF,1121,(*),,,,X,,,,SI,11,N/A,N/A,',
    '1684': 'FOGAFIN,1684,(*),,,,,X,,,NO,N/A,N/A,N/A,',
    '1108': 'IRIS CF,1108,(*),,,,X,,,,SI,12,N/A,N/A,',
    '1286': 'JFK COOPERATIVA FINANCIERA,1286,(*),,X,,,,,,SI,14,N/A,N/A,',
    '1070': 'LULO BANK S.A.,1070,22/05/2025,X,,,,,,,SI,12***,N/A,N/A,',
    '1067': 'MI BANCO,1067,(*),X,,,,,,,SI,12,12,N/A,',
    '1801': 'MOVii S.A.,1801,4/05/2026,,,,X,,,,NO,N/A,N/A,10,MOVii',
    '1507': 'NEQUI S.A. COMPAÑÍA DE FINANCIAMIENTO,1507,1/09/2026,,,,X,,,,NO,10 y 11,N/A,10 y 11,NEQUI',
    '1809': 'NU COLOMBIA,1809,1/12/2026,,,,X,,,,NO,8,N/A,N/A,',
    '1811': 'RAPPIPAY,1811,7/02/2026,,,,X,,,,SI,9,N/A,9,RAPPIPAY',
    '1088': 'SIMPLE S.A.,1088,(*),,,,,,X,,SI,N/A,N/A,N/A,',
    '1026': 'TUYA S.A.,1026,12/08/2026,,,,X,,,,NO,N/A,N/A,16,CUENTA DIGITAL TUYA PAY',
}
)

RECORDS: tuple[Participant, ...] = (
    Participant(
        row_number=1,
        name='APORTES EN LÍNEA S.A.',
        code='1084',
        operation_start_date='(*)',
        entity_types=(EntityType.INFORMATION_OPERATOR,),
        supports_debit_transactions=True,
        account_types_and_lengths=AccountTypesAndLengths(
            savings=(),
            checking=(),
            electronic_or_low_value_deposit=(),
        ),
        electronic_or_low_value_deposit_name=None,
        footnotes=('(*)',),
    ),
    Participant(
        row_number=2,
        name='ASOPAGOS',
        code='1086',
        operation_start_date='(*)',
        entity_types=(EntityType.INFORMATION_OPERATOR,),
        supports_debit_transactions=True,
        account_types_and_lengths=AccountTypesAndLengths(
            savings=(),
            checking=(),
            electronic_or_low_value_deposit=(),
        ),
        electronic_or_low_value_deposit_name=None,
        footnotes=('(*)',),
    ),
    Participant(
        row_number=3,
        name='AVAL SOLUCIONES DIGITALES - DALE',
        code='1899',
        operation_start_date=date(2025, 7, 3),
        entity_types=(EntityType.SEDPE,),
        supports_debit_transactions=True,
        account_types_and_lengths=AccountTypesAndLengths(
            savings=(),
            checking=(),
            electronic_or_low_value_deposit=(
                    AccountNumberLengthVariant(
                        lengths=(12,),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
        ),
        electronic_or_low_value_deposit_name='DALE',
        footnotes=(),
    ),
    Participant(
        row_number=4,
        name='BAN100 S.A.',
        code='1058',
        operation_start_date='(*)',
        entity_types=(EntityType.BANK, EntityType.INFORMATION_OPERATOR),
        supports_debit_transactions=True,
        account_types_and_lengths=AccountTypesAndLengths(
            savings=(
                    AccountNumberLengthVariant(
                        lengths=(13,),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
            checking=(
                    AccountNumberLengthVariant(
                        lengths=(13,),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
            electronic_or_low_value_deposit=(),
        ),
        electronic_or_low_value_deposit_name=None,
        footnotes=('(*)',),
    ),
    Participant(
        row_number=5,
        name='BANCAMÍA',
        code='1059',
        operation_start_date='(*)',
        entity_types=(EntityType.BANK,),
        supports_debit_transactions=False,
        account_types_and_lengths=AccountTypesAndLengths(
            savings=(
                    AccountNumberLengthVariant(
                        lengths=(16,),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
            checking=(),
            electronic_or_low_value_deposit=(
                    AccountNumberLengthVariant(
                        lengths=(),
                        footnote_markers=('****',),
                        scope=AccountNumberLengthScope.ELECTRONIC_DEPOSIT_NOT_ENABLED_IN_CENIT,
                    ),
                ),
        ),
        electronic_or_low_value_deposit_name=None,
        footnotes=('(*)', '(****)'),
    ),
    Participant(
        row_number=6,
        name='BANCO AGRARIO DE COLOMBIA',
        code='1040',
        operation_start_date='(*)',
        entity_types=(EntityType.BANK, EntityType.INFORMATION_OPERATOR),
        supports_debit_transactions=True,
        account_types_and_lengths=AccountTypesAndLengths(
            savings=(
                    AccountNumberLengthVariant(
                        lengths=(12,),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
            checking=(
                    AccountNumberLengthVariant(
                        lengths=(12,),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
            electronic_or_low_value_deposit=(
                    AccountNumberLengthVariant(
                        lengths=(),
                        footnote_markers=('****',),
                        scope=AccountNumberLengthScope.ELECTRONIC_DEPOSIT_NOT_ENABLED_IN_CENIT,
                    ),
                ),
        ),
        electronic_or_low_value_deposit_name=None,
        footnotes=('(*)', '(****)'),
    ),
    Participant(
        row_number=7,
        name='BANCO AV VILLAS',
        code='1052',
        operation_start_date='(*)',
        entity_types=(EntityType.BANK, EntityType.INFORMATION_OPERATOR),
        supports_debit_transactions=True,
        account_types_and_lengths=AccountTypesAndLengths(
            savings=(
                    AccountNumberLengthVariant(
                        lengths=(9,),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
            checking=(
                    AccountNumberLengthVariant(
                        lengths=(9,),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
            electronic_or_low_value_deposit=(
                    AccountNumberLengthVariant(
                        lengths=(9,),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
        ),
        electronic_or_low_value_deposit_name='DEPÓSITOS DIGITALES',
        footnotes=('(*)',),
    ),
    Participant(
        row_number=8,
        name='BANCO BANCOOMEVA',
        code='1061',
        operation_start_date='(*)',
        entity_types=(EntityType.BANK, EntityType.INFORMATION_OPERATOR),
        supports_debit_transactions=True,
        account_types_and_lengths=AccountTypesAndLengths(
            savings=(
                    AccountNumberLengthVariant(
                        lengths=(12,),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
            checking=(
                    AccountNumberLengthVariant(
                        lengths=(12,),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
            electronic_or_low_value_deposit=(
                    AccountNumberLengthVariant(
                        lengths=(),
                        footnote_markers=('****',),
                        scope=AccountNumberLengthScope.ELECTRONIC_DEPOSIT_NOT_ENABLED_IN_CENIT,
                    ),
                ),
        ),
        electronic_or_low_value_deposit_name=None,
        footnotes=('(*)', '(****)'),
    ),
    Participant(
        row_number=9,
        name='BANCO BBVA',
        code='1013',
        operation_start_date='(*)',
        entity_types=(EntityType.BANK, EntityType.INFORMATION_OPERATOR),
        supports_debit_transactions=True,
        account_types_and_lengths=AccountTypesAndLengths(
            savings=(
                    AccountNumberLengthVariant(
                        lengths=(5, 7, 13),
                        footnote_markers=('**',),
                        scope=AccountNumberLengthScope.SPECIAL_COLLECTION_AGREEMENT,
                    ),
                    AccountNumberLengthVariant(
                        lengths=(9, 10, 12, 14, 16),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
            checking=(
                    AccountNumberLengthVariant(
                        lengths=(5, 7),
                        footnote_markers=('**',),
                        scope=AccountNumberLengthScope.SPECIAL_COLLECTION_AGREEMENT,
                    ),
                    AccountNumberLengthVariant(
                        lengths=(9, 10, 12, 14, 16),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
            electronic_or_low_value_deposit=(
                    AccountNumberLengthVariant(
                        lengths=(10,),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
        ),
        electronic_or_low_value_deposit_name='DINERO MOVIL',
        footnotes=('(*)', '(**)'),
    ),
    Participant(
        row_number=10,
        name='BANCO CAJA SOCIAL',
        code='1032',
        operation_start_date='(*)',
        entity_types=(EntityType.BANK, EntityType.INFORMATION_OPERATOR),
        supports_debit_transactions=True,
        account_types_and_lengths=AccountTypesAndLengths(
            savings=(
                    AccountNumberLengthVariant(
                        lengths=(11, 13),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
            checking=(
                    AccountNumberLengthVariant(
                        lengths=(11,),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
            electronic_or_low_value_deposit=(
                    AccountNumberLengthVariant(
                        lengths=(),
                        footnote_markers=('****',),
                        scope=AccountNumberLengthScope.ELECTRONIC_DEPOSIT_NOT_ENABLED_IN_CENIT,
                    ),
                ),
        ),
        electronic_or_low_value_deposit_name=None,
        footnotes=('(*)', '(****)'),
    ),
    Participant(
        row_number=11,
        name='BANCO CITIBANK',
        code='1009',
        operation_start_date='(*)',
        entity_types=(EntityType.BANK, EntityType.INFORMATION_OPERATOR),
        supports_debit_transactions=True,
        account_types_and_lengths=AccountTypesAndLengths(
            savings=(
                    AccountNumberLengthVariant(
                        lengths=(10,),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
            checking=(
                    AccountNumberLengthVariant(
                        lengths=(10,),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
            electronic_or_low_value_deposit=(),
        ),
        electronic_or_low_value_deposit_name=None,
        footnotes=('(*)',),
    ),
    Participant(
        row_number=12,
        name='BANCO COOPCENTRAL',
        code='1066',
        operation_start_date='(*)',
        entity_types=(EntityType.BANK, EntityType.INFORMATION_OPERATOR),
        supports_debit_transactions=True,
        account_types_and_lengths=AccountTypesAndLengths(
            savings=(
                    AccountNumberLengthVariant(
                        lengths=(9, 13),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
            checking=(
                    AccountNumberLengthVariant(
                        lengths=(9, 13),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
            electronic_or_low_value_deposit=(
                    AccountNumberLengthVariant(
                        lengths=(9, 13),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
        ),
        electronic_or_low_value_deposit_name='LETMI',
        footnotes=('(*)',),
    ),
    Participant(
        row_number=13,
        name='BANCO DAVIVIENDA',
        code='1051',
        operation_start_date='(*)',
        entity_types=(EntityType.BANK, EntityType.INFORMATION_OPERATOR),
        supports_debit_transactions=True,
        account_types_and_lengths=AccountTypesAndLengths(
            savings=(
                    AccountNumberLengthVariant(
                        lengths=(16,),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
            checking=(
                    AccountNumberLengthVariant(
                        lengths=(16,),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
            electronic_or_low_value_deposit=(
                    AccountNumberLengthVariant(
                        lengths=(10,),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
        ),
        electronic_or_low_value_deposit_name='DAVIPLATA',
        footnotes=('(*)',),
    ),
    Participant(
        row_number=14,
        name='BANCO DE BOGOTÁ',
        code='1001',
        operation_start_date='(*)',
        entity_types=(EntityType.BANK, EntityType.INFORMATION_OPERATOR),
        supports_debit_transactions=True,
        account_types_and_lengths=AccountTypesAndLengths(
            savings=(
                    AccountNumberLengthVariant(
                        lengths=(9,),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
            checking=(
                    AccountNumberLengthVariant(
                        lengths=(9,),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
            electronic_or_low_value_deposit=(),
        ),
        electronic_or_low_value_deposit_name=None,
        footnotes=('(*)',),
    ),
    Participant(
        row_number=15,
        name='BANCO DE OCCIDENTE',
        code='1023',
        operation_start_date='(*)',
        entity_types=(EntityType.BANK, EntityType.INFORMATION_OPERATOR),
        supports_debit_transactions=True,
        account_types_and_lengths=AccountTypesAndLengths(
            savings=(
                    AccountNumberLengthVariant(
                        lengths=(9,),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
            checking=(
                    AccountNumberLengthVariant(
                        lengths=(9,),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
            electronic_or_low_value_deposit=(),
        ),
        electronic_or_low_value_deposit_name=None,
        footnotes=('(*)',),
    ),
    Participant(
        row_number=16,
        name='BANCO FALABELLA',
        code='1062',
        operation_start_date='(*)',
        entity_types=(EntityType.BANK, EntityType.INFORMATION_OPERATOR),
        supports_debit_transactions=True,
        account_types_and_lengths=AccountTypesAndLengths(
            savings=(
                    AccountNumberLengthVariant(
                        lengths=(12,),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
            checking=(
                    AccountNumberLengthVariant(
                        lengths=(12,),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
            electronic_or_low_value_deposit=(),
        ),
        electronic_or_low_value_deposit_name=None,
        footnotes=('(*)',),
    ),
    Participant(
        row_number=17,
        name='BANCO FINANDINA',
        code='1063',
        operation_start_date='(*)',
        entity_types=(EntityType.BANK,),
        supports_debit_transactions=True,
        account_types_and_lengths=AccountTypesAndLengths(
            savings=(
                    AccountNumberLengthVariant(
                        lengths=(10,),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
            checking=(
                    AccountNumberLengthVariant(
                        lengths=(10,),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
            electronic_or_low_value_deposit=(),
        ),
        electronic_or_low_value_deposit_name=None,
        footnotes=('(*)',),
    ),
    Participant(
        row_number=18,
        name='BANCO GNB SUDAMERIS',
        code='1012',
        operation_start_date='(*)',
        entity_types=(EntityType.BANK, EntityType.INFORMATION_OPERATOR),
        supports_debit_transactions=True,
        account_types_and_lengths=AccountTypesAndLengths(
            savings=(
                    AccountNumberLengthVariant(
                        lengths=(18,),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
            checking=(
                    AccountNumberLengthVariant(
                        lengths=(18,),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
            electronic_or_low_value_deposit=(),
        ),
        electronic_or_low_value_deposit_name=None,
        footnotes=('(*)',),
    ),
    Participant(
        row_number=19,
        name='BANCO ITAÚ',
        code='1006',
        operation_start_date='(*)',
        entity_types=(EntityType.BANK, EntityType.INFORMATION_OPERATOR),
        supports_debit_transactions=True,
        account_types_and_lengths=AccountTypesAndLengths(
            savings=(
                    AccountNumberLengthVariant(
                        lengths=(9,),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
            checking=(
                    AccountNumberLengthVariant(
                        lengths=(9,),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
            electronic_or_low_value_deposit=(),
        ),
        electronic_or_low_value_deposit_name=None,
        footnotes=('(*)',),
    ),
    Participant(
        row_number=20,
        name='BANCO JP MORGAN',
        code='1071',
        operation_start_date='(*)',
        entity_types=(EntityType.BANK,),
        supports_debit_transactions=True,
        account_types_and_lengths=AccountTypesAndLengths(
            savings=(),
            checking=(
                    AccountNumberLengthVariant(
                        lengths=(10,),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
            electronic_or_low_value_deposit=(),
        ),
        electronic_or_low_value_deposit_name=None,
        footnotes=('(*)',),
    ),
    Participant(
        row_number=21,
        name='BANCO MUNDO MUJER',
        code='1047',
        operation_start_date='(*)',
        entity_types=(EntityType.BANK,),
        supports_debit_transactions=True,
        account_types_and_lengths=AccountTypesAndLengths(
            savings=(
                    AccountNumberLengthVariant(
                        lengths=(14,),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
            checking=(),
            electronic_or_low_value_deposit=(),
        ),
        electronic_or_low_value_deposit_name=None,
        footnotes=('(*)',),
    ),
    Participant(
        row_number=22,
        name='BANCO PICHINCHA',
        code='1060',
        operation_start_date='(*)',
        entity_types=(EntityType.BANK, EntityType.INFORMATION_OPERATOR),
        supports_debit_transactions=False,
        account_types_and_lengths=AccountTypesAndLengths(
            savings=(
                    AccountNumberLengthVariant(
                        lengths=(9,),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
            checking=(
                    AccountNumberLengthVariant(
                        lengths=(9,),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
            electronic_or_low_value_deposit=(),
        ),
        electronic_or_low_value_deposit_name=None,
        footnotes=('(*)',),
    ),
    Participant(
        row_number=23,
        name='BANCO POPULAR',
        code='1002',
        operation_start_date='(*)',
        entity_types=(EntityType.BANK, EntityType.INFORMATION_OPERATOR),
        supports_debit_transactions=True,
        account_types_and_lengths=AccountTypesAndLengths(
            savings=(
                    AccountNumberLengthVariant(
                        lengths=(12,),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
            checking=(
                    AccountNumberLengthVariant(
                        lengths=(12,),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
            electronic_or_low_value_deposit=(),
        ),
        electronic_or_low_value_deposit_name=None,
        footnotes=('(*)',),
    ),
    Participant(
        row_number=24,
        name='BANCO REPÚBLICA',
        code='1000',
        operation_start_date='(*)',
        entity_types=(EntityType.BANK,),
        supports_debit_transactions=False,
        account_types_and_lengths=AccountTypesAndLengths(
            savings=(),
            checking=(),
            electronic_or_low_value_deposit=(),
        ),
        electronic_or_low_value_deposit_name=None,
        footnotes=('(*)',),
    ),
    Participant(
        row_number=25,
        name='BANCO SANTANDER DE NEGOCIOS',
        code='1065',
        operation_start_date='(*)',
        entity_types=(EntityType.BANK,),
        supports_debit_transactions=True,
        account_types_and_lengths=AccountTypesAndLengths(
            savings=(
                    AccountNumberLengthVariant(
                        lengths=(9,),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
            checking=(
                    AccountNumberLengthVariant(
                        lengths=(9,),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
            electronic_or_low_value_deposit=(),
        ),
        electronic_or_low_value_deposit_name=None,
        footnotes=('(*)',),
    ),
    Participant(
        row_number=26,
        name='BANCO SERFINANZA',
        code='1069',
        operation_start_date='(*)',
        entity_types=(EntityType.BANK,),
        supports_debit_transactions=True,
        account_types_and_lengths=AccountTypesAndLengths(
            savings=(
                    AccountNumberLengthVariant(
                        lengths=(12,),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
            checking=(
                    AccountNumberLengthVariant(
                        lengths=(12,),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
            electronic_or_low_value_deposit=(
                    AccountNumberLengthVariant(
                        lengths=(12,),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
        ),
        electronic_or_low_value_deposit_name='CLICuenta',
        footnotes=('(*)',),
    ),
    Participant(
        row_number=27,
        name='BANCOLOMBIA',
        code='1007',
        operation_start_date='(*)',
        entity_types=(EntityType.BANK, EntityType.INFORMATION_OPERATOR),
        supports_debit_transactions=True,
        account_types_and_lengths=AccountTypesAndLengths(
            savings=(
                    AccountNumberLengthVariant(
                        lengths=(11,),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
            checking=(
                    AccountNumberLengthVariant(
                        lengths=(11,),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
            electronic_or_low_value_deposit=(
                    AccountNumberLengthVariant(
                        lengths=(11,),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
        ),
        electronic_or_low_value_deposit_name='Bancolombia',
        footnotes=('(*)',),
    ),
    Participant(
        row_number=28,
        name='BNP PARIBAS',
        code='1042',
        operation_start_date='(*)',
        entity_types=(EntityType.FINANCIAL_CORPORATION,),
        supports_debit_transactions=True,
        account_types_and_lengths=AccountTypesAndLengths(
            savings=(
                    AccountNumberLengthVariant(
                        lengths=(16,),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
            checking=(),
            electronic_or_low_value_deposit=(),
        ),
        electronic_or_low_value_deposit_name=None,
        footnotes=('(*)',),
    ),
    Participant(
        row_number=29,
        name='COLTEFINANCIERA',
        code='1370',
        operation_start_date='(*)',
        entity_types=(EntityType.FINANCING_COMPANY,),
        supports_debit_transactions=True,
        account_types_and_lengths=AccountTypesAndLengths(
            savings=(
                    AccountNumberLengthVariant(
                        lengths=(10,),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
            checking=(),
            electronic_or_low_value_deposit=(),
        ),
        electronic_or_low_value_deposit_name=None,
        footnotes=('(*)',),
    ),
    Participant(
        row_number=30,
        name='COMPENSAR',
        code='1083',
        operation_start_date='(*)',
        entity_types=(EntityType.INFORMATION_OPERATOR,),
        supports_debit_transactions=True,
        account_types_and_lengths=AccountTypesAndLengths(
            savings=(),
            checking=(),
            electronic_or_low_value_deposit=(),
        ),
        electronic_or_low_value_deposit_name=None,
        footnotes=('(*)',),
    ),
    Participant(
        row_number=31,
        name='CONFIAR COOPERATIVA FINANCIERA',
        code='1292',
        operation_start_date='(*)',
        entity_types=(EntityType.FINANCIAL_COOPERATIVE,),
        supports_debit_transactions=True,
        account_types_and_lengths=AccountTypesAndLengths(
            savings=(
                    AccountNumberLengthVariant(
                        lengths=(9,),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
            checking=(),
            electronic_or_low_value_deposit=(),
        ),
        electronic_or_low_value_deposit_name=None,
        footnotes=('(*)',),
    ),
    Participant(
        row_number=32,
        name='COOPERATIVA FINANCIERA DE ANTIOQUIA',
        code='1283',
        operation_start_date='(*)',
        entity_types=(EntityType.FINANCIAL_COOPERATIVE,),
        supports_debit_transactions=False,
        account_types_and_lengths=AccountTypesAndLengths(
            savings=(
                    AccountNumberLengthVariant(
                        lengths=(11,),
                        footnote_markers=('***',),
                        scope=AccountNumberLengthScope.INCLUDES_LEADING_ZEROS,
                    ),
                ),
            checking=(),
            electronic_or_low_value_deposit=(
                    AccountNumberLengthVariant(
                        lengths=(10,),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
        ),
        electronic_or_low_value_deposit_name='CFA EXPRESS',
        footnotes=('(*)', '(***)'),
    ),
    Participant(
        row_number=33,
        name='COTRAFA',
        code='1289',
        operation_start_date='(*)',
        entity_types=(EntityType.FINANCIAL_COOPERATIVE,),
        supports_debit_transactions=True,
        account_types_and_lengths=AccountTypesAndLengths(
            savings=(
                    AccountNumberLengthVariant(
                        lengths=(13,),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
            checking=(),
            electronic_or_low_value_deposit=(),
        ),
        electronic_or_low_value_deposit_name=None,
        footnotes=('(*)',),
    ),
    Participant(
        row_number=34,
        name='CREZCAMOS COMPAÑÍA DE FINANCIAMIENTO',
        code='1816',
        operation_start_date=date(2025, 9, 1),
        entity_types=(EntityType.FINANCING_COMPANY,),
        supports_debit_transactions=False,
        account_types_and_lengths=AccountTypesAndLengths(
            savings=(
                    AccountNumberLengthVariant(
                        lengths=(11,),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
            checking=(),
            electronic_or_low_value_deposit=(
                    AccountNumberLengthVariant(
                        lengths=(10,),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
        ),
        electronic_or_low_value_deposit_name='MOSI',
        footnotes=(),
    ),
    Participant(
        row_number=35,
        name='DAVIBANK',
        code='1019',
        operation_start_date='(*)',
        entity_types=(EntityType.BANK, EntityType.INFORMATION_OPERATOR),
        supports_debit_transactions=True,
        account_types_and_lengths=AccountTypesAndLengths(
            savings=(
                    AccountNumberLengthVariant(
                        lengths=(10,),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
            checking=(
                    AccountNumberLengthVariant(
                        lengths=(10,),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
            electronic_or_low_value_deposit=(),
        ),
        electronic_or_low_value_deposit_name=None,
        footnotes=('(*)',),
    ),
    Participant(
        row_number=36,
        name='DECEVAL',
        code='1550',
        operation_start_date='(*)',
        entity_types=(EntityType.GOVERNMENT_ENTITY,),
        supports_debit_transactions=False,
        account_types_and_lengths=AccountTypesAndLengths(
            savings=(),
            checking=(),
            electronic_or_low_value_deposit=(),
        ),
        electronic_or_low_value_deposit_name=None,
        footnotes=('(*)',),
    ),
    Participant(
        row_number=37,
        name='DGCPTN',
        code='1683',
        operation_start_date='(*)',
        entity_types=(EntityType.GOVERNMENT_ENTITY,),
        supports_debit_transactions=False,
        account_types_and_lengths=AccountTypesAndLengths(
            savings=(),
            checking=(),
            electronic_or_low_value_deposit=(),
        ),
        electronic_or_low_value_deposit_name=None,
        footnotes=('(*)',),
    ),
    Participant(
        row_number=38,
        name='DGCPTN – REGALÍAS',
        code='1685',
        operation_start_date='(*)',
        entity_types=(EntityType.GOVERNMENT_ENTITY,),
        supports_debit_transactions=False,
        account_types_and_lengths=AccountTypesAndLengths(
            savings=(),
            checking=(),
            electronic_or_low_value_deposit=(),
        ),
        electronic_or_low_value_deposit_name=None,
        footnotes=('(*)',),
    ),
    Participant(
        row_number=39,
        name='ENLACE OPERATIVO',
        code='1089',
        operation_start_date='(*)',
        entity_types=(EntityType.INFORMATION_OPERATOR,),
        supports_debit_transactions=True,
        account_types_and_lengths=AccountTypesAndLengths(
            savings=(),
            checking=(),
            electronic_or_low_value_deposit=(),
        ),
        electronic_or_low_value_deposit_name=None,
        footnotes=('(*)',),
    ),
    Participant(
        row_number=40,
        name='FINANCIERA JURISCOOP CF',
        code='1121',
        operation_start_date='(*)',
        entity_types=(EntityType.FINANCING_COMPANY,),
        supports_debit_transactions=True,
        account_types_and_lengths=AccountTypesAndLengths(
            savings=(
                    AccountNumberLengthVariant(
                        lengths=(11,),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
            checking=(),
            electronic_or_low_value_deposit=(),
        ),
        electronic_or_low_value_deposit_name=None,
        footnotes=('(*)',),
    ),
    Participant(
        row_number=41,
        name='FOGAFIN',
        code='1684',
        operation_start_date='(*)',
        entity_types=(EntityType.GOVERNMENT_ENTITY,),
        supports_debit_transactions=False,
        account_types_and_lengths=AccountTypesAndLengths(
            savings=(),
            checking=(),
            electronic_or_low_value_deposit=(),
        ),
        electronic_or_low_value_deposit_name=None,
        footnotes=('(*)',),
    ),
    Participant(
        row_number=42,
        name='IRIS CF',
        code='1108',
        operation_start_date='(*)',
        entity_types=(EntityType.FINANCING_COMPANY,),
        supports_debit_transactions=True,
        account_types_and_lengths=AccountTypesAndLengths(
            savings=(
                    AccountNumberLengthVariant(
                        lengths=(12,),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
            checking=(),
            electronic_or_low_value_deposit=(),
        ),
        electronic_or_low_value_deposit_name=None,
        footnotes=('(*)',),
    ),
    Participant(
        row_number=43,
        name='JFK COOPERATIVA FINANCIERA',
        code='1286',
        operation_start_date='(*)',
        entity_types=(EntityType.FINANCIAL_COOPERATIVE,),
        supports_debit_transactions=True,
        account_types_and_lengths=AccountTypesAndLengths(
            savings=(
                    AccountNumberLengthVariant(
                        lengths=(14,),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
            checking=(),
            electronic_or_low_value_deposit=(),
        ),
        electronic_or_low_value_deposit_name=None,
        footnotes=('(*)',),
    ),
    Participant(
        row_number=44,
        name='LULO BANK S.A.',
        code='1070',
        operation_start_date=date(2025, 5, 22),
        entity_types=(EntityType.BANK,),
        supports_debit_transactions=True,
        account_types_and_lengths=AccountTypesAndLengths(
            savings=(
                    AccountNumberLengthVariant(
                        lengths=(12,),
                        footnote_markers=('***',),
                        scope=AccountNumberLengthScope.INCLUDES_LEADING_ZEROS,
                    ),
                ),
            checking=(),
            electronic_or_low_value_deposit=(),
        ),
        electronic_or_low_value_deposit_name=None,
        footnotes=('(***)',),
    ),
    Participant(
        row_number=45,
        name='MI BANCO',
        code='1067',
        operation_start_date='(*)',
        entity_types=(EntityType.BANK,),
        supports_debit_transactions=True,
        account_types_and_lengths=AccountTypesAndLengths(
            savings=(
                    AccountNumberLengthVariant(
                        lengths=(12,),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
            checking=(
                    AccountNumberLengthVariant(
                        lengths=(12,),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
            electronic_or_low_value_deposit=(),
        ),
        electronic_or_low_value_deposit_name=None,
        footnotes=('(*)',),
    ),
    Participant(
        row_number=46,
        name='MOVii S.A.',
        code='1801',
        operation_start_date=date(2026, 5, 4),
        entity_types=(EntityType.FINANCING_COMPANY,),
        supports_debit_transactions=False,
        account_types_and_lengths=AccountTypesAndLengths(
            savings=(),
            checking=(),
            electronic_or_low_value_deposit=(
                    AccountNumberLengthVariant(
                        lengths=(10,),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
        ),
        electronic_or_low_value_deposit_name='MOVii',
        footnotes=(),
    ),
    Participant(
        row_number=47,
        name='NEQUI S.A. COMPAÑÍA DE FINANCIAMIENTO',
        code='1507',
        operation_start_date=date(2026, 9, 1),
        entity_types=(EntityType.FINANCING_COMPANY,),
        supports_debit_transactions=False,
        account_types_and_lengths=AccountTypesAndLengths(
            savings=(
                    AccountNumberLengthVariant(
                        lengths=(10, 11),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
            checking=(),
            electronic_or_low_value_deposit=(
                    AccountNumberLengthVariant(
                        lengths=(10, 11),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
        ),
        electronic_or_low_value_deposit_name='NEQUI',
        footnotes=(),
    ),
    Participant(
        row_number=48,
        name='NU COLOMBIA',
        code='1809',
        operation_start_date=date(2026, 12, 1),
        operation_start_note=None,
        entity_types=(EntityType.FINANCING_COMPANY,),
        supports_debit_transactions=False,
        account_capabilities=AccountCapabilities(
            savings_account_number_lengths=(
                    AccountNumberLengthVariant(
                        lengths=(8,),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
            checking_account_number_lengths=(),
            electronic_or_low_value_deposit_number_lengths=(),
        ),
        electronic_or_low_value_deposit_name=None,
        footnotes=(),
    ),
    Participant(
        row_number=49,
        name='RAPPIPAY',
        code='1811',
        operation_start_date=date(2026, 2, 7),
        entity_types=(EntityType.FINANCING_COMPANY,),
        supports_debit_transactions=True,
        account_types_and_lengths=AccountTypesAndLengths(
            savings=(
                    AccountNumberLengthVariant(
                        lengths=(9,),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
            checking=(),
            electronic_or_low_value_deposit=(
                    AccountNumberLengthVariant(
                        lengths=(9,),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
        ),
        electronic_or_low_value_deposit_name='RAPPIPAY',
        footnotes=(),
    ),
    Participant(
        row_number=50,
        name='SIMPLE S.A.',
        code='1088',
        operation_start_date='(*)',
        entity_types=(EntityType.INFORMATION_OPERATOR,),
        supports_debit_transactions=True,
        account_types_and_lengths=AccountTypesAndLengths(
            savings=(),
            checking=(),
            electronic_or_low_value_deposit=(),
        ),
        electronic_or_low_value_deposit_name=None,
        footnotes=('(*)',),
    ),
    Participant(
        row_number=51,
        name='TUYA S.A.',
        code='1026',
        operation_start_date=date(2026, 8, 12),
        entity_types=(EntityType.FINANCING_COMPANY,),
        supports_debit_transactions=False,
        account_types_and_lengths=AccountTypesAndLengths(
            savings=(),
            checking=(),
            electronic_or_low_value_deposit=(
                    AccountNumberLengthVariant(
                        lengths=(16,),
                        footnote_markers=(),
                        scope=AccountNumberLengthScope.STANDARD,
                    ),
                ),
        ),
        electronic_or_low_value_deposit_name='CUENTA DIGITAL TUYA PAY',
        footnotes=(),
    ),
)

CODES_BY_CENIT_CODE: Mapping[str, Participant] = MappingProxyType(
    {record.code: record for record in RECORDS}
)
CODES_BY_NAME: Mapping[str, Participant] = MappingProxyType(
    {normalize_name(record.name): record for record in RECORDS}
)
TOTALS = Totals(
    participants=51,
    entity_types=EntityTypeTotals(
        bank=27,
        financial_cooperative=4,
        financial_corporation=1,
        financing_company=9,
        government_entity=4,
        information_operator=23,
        sedpe=1,
    ),
)
