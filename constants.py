import re
from googletrans.constants import LANGUAGES

MAX_RETRY = 5
MAX_FILES = 50
MAX_CHARS = 32

REGEX = {
    "title": re.compile(r'(?<=\btitle: )\"(?:[^"\\]|\\.)*\"', flags=re.MULTILINE),
    "subtitle": re.compile(r'(?<=\bsubtitle: )\"(?:[^"\\]|\\.)*\"', flags=re.MULTILINE),
    "description": re.compile(r'(?<=\bdescription: )\[[\s\S.]*?\]\s', flags=re.MULTILINE),
    "string": re.compile(r'(?<=\")(?:(?=\\?)\\?.)*?(?=\")', flags=re.MULTILINE),
    "strip": re.compile('\W+')
}

MESSAGES = {
    "convert_quests": "Converting quests... ({progress:.2f}%)",
    "translate_quests": "Translating quests... ({progress:.2f}%)",
    "convert_success": "Successfully converted!",
    "translate_success": "Successfully translated!",
    "convert_error": "An error occurred while converting quests: {e}",
    "translate_error": "An error occurred while translating quests: {e}",
    "download_button": "Download {file_name}",
    "uploader_label": f"Upload all the FTB Quests files (.snbt) contained in the modpack to localize. (Max: {MAX_FILES} files)",
    "uploader_help": "You can upload multiple files at once by selecting multiple files in the file selection dialog.",
    "uploader_empty": "You can find the FTB Quests files (.snbt) in the `config/ftbquests/quests` folder of the modpack.",
    "uploader_exceed": f"You can upload up to {MAX_FILES} files at once.",
    "modpack_label": "Enter the shortened name of the modpack. [Example: All the Mods 9 → atm9]",
    "modpack_help": "This name will be used as the namespace for localization.",
    "auto_translate_label": "Do you want to translate the quests automatically using Google Translate?",
    "auto_translate_help": "If you select 'Yes', the quests will be translated automatically using Google Translate.",
    "src_label": "Select the language of the quests you uploaded.",
    "src_help": "This is the language of the quests you uploaded.",
    "dest_label": "Select the language you want to translate the quests into.",
    "dest_help": "This is the language you want to translate the quests into.",
    "localize_label": "Start localization",
    "localize_help": "Click this button to start localization.",
    "localize_start": "Localization started!",
    "localize_finish": "Localization finished!",
    "apply_manual_1": "1. Download `localized_snbt.zip`. (Click the button below)",
    "apply_manual_2": "2. Extract `localized_snbt.zip` and replace the original `.snbt` files in `config/ftbquests/quests` folder with the extracted files.",
    "apply_manual_3_1": "3. Download `{src}.json` and `{dest}.json`. (Click the buttons below)",
    "apply_manual_4_1": "4. Put `{src}.json` and `{dest}.json` in `kubejs/assets/kubejs/lang` folder.",
    "apply_manual_5_1": "5. Done! If you want to fix mistranslated text, edit `{dest}.json`.",
    "apply_manual_3_2": "3. Download `{src}.json`. (Click the button below)",
    "apply_manual_4_2": "4. Put `{src}.json` in `kubejs/assets/kubejs/lang` folder.",
    "apply_manual_5_2": "5. Done!",
    "apply_manual_warning": "Do not change `{src}.json`.",
    "add_manual_1": "1. Download `template_lang.json`. (Click the button below)",
    "add_manual_2": "2. Rename `template_lang.json` to `<language>.json`. [Example: `en_us.json`]",
    "add_manual_3": "3. Translate the text in `{src}.json` and put the translated text in `<language>.json`. You can use this localization tool or any translator to translate the text.",
    "add_manual_4": "4. Put `<language>.json` in `kubejs/assets/kubejs/lang` folder.",
    "add_manual_5": "5. Done!",
    "add_manual_warning": "Do not change `{src}.json`. The translated text should be put in `<language>.json`.",
    "lang_link_label": "List of Minecraft languages",
    "lang_link_url": "https://minecraft.fandom.com/wiki/Language#Languages",
    "lang_link_help": "Click this link to see the list of Minecraft languages.",
}

MINECRAFT_LOCALES = [
    "af_za",
    "ar_sa",
    "ast_es",
    "az_az",
    "ba_ru",
    "bar",
    "be_by",
    "bg_bg",
    "br_fr",
    "brb",
    "bs_ba",
    "ca_es",
    "cs_cz",
    "cy_gb",
    "da_dk",
    "de_at",
    "de_ch",
    "de_de",
    "el_gr",
    "en_au",
    "en_ca",
    "en_gb",
    "en_nz",
    "en_pt",
    "en_ud",
    "en_us",
    "enp",
    "enws",
    "eo_uy",
    "es_ar",
    "es_cl",
    "es_ec",
    "es_es",
    "es_mx",
    "es_uy",
    "es_ve",
    "esan",
    "et_ee",
    "eu_es",
    "fa_ir",
    "fi_fi",
    "fil_ph",
    "fo_fo",
    "fr_ca",
    "fr_fr",
    "fra_de",
    "fur_it",
    "fy_nl",
    "ga_ie",
    "gd_gb",
    "gl_es",
    "haw_us",
    "he_il",
    "hi_in",
    "hr_hr",
    "hu_hu",
    "hy_am",
    "id_id",
    "ig_ng",
    "io_en",
    "is_is",
    "isv",
    "it_it",
    "ja_jp",
    "jbo_en",
    "ka_ge",
    "kk_kz",
    "kn_in",
    "ko_kr",
    "ksh",
    "kw_gb",
    "la_la",
    "lb_lu",
    "li_li",
    "lmo",
    "lo_la",
    "lol_us",
    "lt_lt",
    "lv_lv",
    "lzh",
    "mk_mk",
    "mn_mn",
    "ms_my",
    "mt_mt",
    "nah",
    "nds_de",
    "nl_be",
    "nl_nl",
    "nn_no",
    "no_no",
    "oc_fr",
    "ovd",
    "pl_pl",
    "pt_br",
    "pt_pt",
    "qya_aa",
    "ro_ro",
    "rpr",
    "ru_ru",
    "ry_ua",
    "sah_sah",
    "se_no",
    "sk_sk",
    "sl_si",
    "so_so",
    "sq_al",
    "sr_cs",
    "sr_sp",
    "sv_se",
    "sxu",
    "szl",
    "ta_in",
    "th_th",
    "tl_ph",
    "tlh_aa",
    "tok",
    "tr_tr",
    "tt_ru",
    "uk_ua",
    "val_es",
    "vec_it",
    "vi_vn",
    "yi_de",
    "yo_ng",
    "zh_cn",
    "zh_hk",
    "zh_tw",
    "zlm_arab"
]

MINECRAFT_LANGUAGES = {
    "af_za": "Afrikaans",
    "ar_sa": "Arabic",
    "az_az": "Azerbaijani",
    "be_by": "Belarusian",
    "bg_bg": "Bulgarian",
    "bs_ba": "Bosnian",
    "ca_es": "Catalan",
    "cs_cz": "Czech",
    "cy_gb": "Welsh",
    "da_dk": "Danish",
    "de_at": "German",
    "de_ch": "German",
    "de_de": "German",
    "el_gr": "Greek",
    "en_au": "English",
    "en_ca": "English",
    "en_gb": "English",
    "en_nz": "English",
    "en_pt": "English",
    "en_ud": "English",
    "en_us": "English",
    "eo_uy": "Esperanto",
    "es_ar": "Spanish",
    "es_cl": "Spanish",
    "es_ec": "Spanish",
    "es_es": "Spanish",
    "es_mx": "Spanish",
    "es_uy": "Spanish",
    "es_ve": "Spanish",
    "et_ee": "Estonian",
    "eu_es": "Basque",
    "fa_ir": "Persian",
    "fi_fi": "Finnish",
    "fr_ca": "French",
    "fr_fr": "French",
    "fy_nl": "Frisian",
    "ga_ie": "Irish",
    "gd_gb": "Scots Gaelic",
    "gl_es": "Galician",
    "haw_us": "Hawaiian",
    "he_il": "Hebrew",
    "hi_in": "Hindi",
    "hr_hr": "Croatian",
    "hu_hu": "Hungarian",
    "hy_am": "Armenian",
    "id_id": "Indonesian",
    "ig_ng": "Igbo",
    "is_is": "Icelandic",
    "it_it": "Italian",
    "ja_jp": "Japanese",
    "ka_ge": "Georgian",
    "kk_kz": "Kazakh",
    "kn_in": "Kannada",
    "ko_kr": "Korean",
    "la_la": "Latin",
    "lb_lu": "Luxembourgish",
    "lo_la": "Lao",
    "lt_lt": "Lithuanian",
    "lv_lv": "Latvian",
    "mk_mk": "Macedonian",
    "mn_mn": "Mongolian",
    "ms_my": "Malay",
    "mt_mt": "Maltese",
    "nl_be": "Dutch",
    "nl_nl": "Dutch",
    "no_no": "Norwegian",
    "pl_pl": "Polish",
    "pt_br": "Portuguese",
    "pt_pt": "Portuguese",
    "ro_ro": "Romanian",
    "ru_ru": "Russian",
    "sk_sk": "Slovak",
    "sl_si": "Slovenian",
    "so_so": "Somali",
    "sq_al": "Albanian",
    "sr_cs": "Serbian",
    "sr_sp": "Serbian",
    "sv_se": "Swedish",
    "ta_in": "Tamil",
    "th_th": "Thai",
    "tl_ph": "Filipino",
    "tr_tr": "Turkish",
    "uk_ua": "Ukrainian",
    "vi_vn": "Vietnamese",
    "yi_de": "Yiddish",
    "yo_ng": "Yoruba",
    "zh_cn": "Chinese (Simplified)",
    "zh_tw": "Chinese (Traditional)"
}

MINECRAFT_TO_GOOGLE = {
    "af_za": "af",
    "ar_sa": "ar",
    "az_az": "az",
    "be_by": "be",
    "bg_bg": "bg",
    "bs_ba": "bs",
    "ca_es": "ca",
    "cs_cz": "cs",
    "cy_gb": "cy",
    "da_dk": "da",
    "de_at": "de",
    "de_ch": "de",
    "de_de": "de",
    "el_gr": "el",
    "en_au": "en",
    "en_ca": "en",
    "en_gb": "en",
    "en_nz": "en",
    "en_pt": "en",
    "en_ud": "en",
    "en_us": "en",
    "eo_uy": "eo",
    "es_ar": "es",
    "es_cl": "es",
    "es_ec": "es",
    "es_es": "es",
    "es_mx": "es",
    "es_uy": "es",
    "es_ve": "es",
    "et_ee": "et",
    "eu_es": "eu",
    "fa_ir": "fa",
    "fi_fi": "fi",
    "fr_ca": "fr",
    "fr_fr": "fr",
    "fy_nl": "fy",
    "ga_ie": "ga",
    "gd_gb": "gd",
    "gl_es": "gl",
    "haw_us": "haw",
    "he_il": "he",
    "hi_in": "hi",
    "hr_hr": "hr",
    "hu_hu": "hu",
    "hy_am": "hy",
    "id_id": "id",
    "ig_ng": "ig",
    "is_is": "is",
    "it_it": "it",
    "ja_jp": "ja",
    "ka_ge": "ka",
    "kk_kz": "kk",
    "kn_in": "kn",
    "ko_kr": "ko",
    "la_la": "la",
    "lb_lu": "lb",
    "lo_la": "lo",
    "lt_lt": "lt",
    "lv_lv": "lv",
    "mk_mk": "mk",
    "mn_mn": "mn",
    "ms_my": "ms",
    "mt_mt": "mt",
    "nl_be": "nl",
    "nl_nl": "nl",
    "no_no": "no",
    "pl_pl": "pl",
    "pt_br": "pt",
    "pt_pt": "pt",
    "ro_ro": "ro",
    "ru_ru": "ru",
    "sk_sk": "sk",
    "sl_si": "sl",
    "so_so": "so",
    "sq_al": "sq",
    "sr_cs": "sr",
    "sr_sp": "sr",
    "sv_se": "sv",
    "ta_in": "ta",
    "th_th": "th",
    "tl_ph": "tl",
    "tr_tr": "tr",
    "uk_ua": "uk",
    "vi_vn": "vi",
    "yi_de": "yi",
    "yo_ng": "yo",
    "zh_cn": "zh-cn",
    "zh_tw": "zh-tw"
}

if __name__ == "__main__":
    MINECRAFT_LANGUAGES = dict()
    MINECRAFT_TO_GOOGLE = dict()
    for lang in MINECRAFT_LOCALES:
        _lang = lang.replace("_", "-")
        if LANGUAGES.get(_lang):
            MINECRAFT_LANGUAGES[lang] = LANGUAGES[_lang].title()
            MINECRAFT_TO_GOOGLE[lang] = _lang
            continue
        _lang = _lang.split("-")[0]
        if LANGUAGES.get(_lang):
            MINECRAFT_LANGUAGES[lang] = LANGUAGES[_lang].title()
            MINECRAFT_TO_GOOGLE[lang] = _lang
            continue