
## Unreleased

- Add validation for collection's spatial intervals
- Add validation for collection's time intervals
- Move `validate_bbox`, `validate_datetime` and `str_to_datetimes` functions from `api.search` to `shared` sub-module
- Improve `bbox` validation for Antimeridian crossing bbox

## 3.2.0 (2025-03-20)

- Move `validate_bbox` and `validate_datetime` field validation functions outside the Search class (to enable re-utilization)
- Remove `Search()._start_date` and ``Search()._end_date` private attributes
- Add `api.search.str_to_datetime(value: str) -> List[Optional[datetime.datetime]]` function

## 3.1.5 (2025-02-28)

- Fix `Search` model to make sure `_start_date` and `_end_date` privateAttr are cleared on model initialization (#72, @sbrunato and @vincentsarago)
- Fix bbox validation to allow anti-meridian crossing (#167, @ujjwal360)
- Add `octet_stream=application/octet-stream` to MimeTypes (#169, @tjellicoe-tpzuk)

## 3.1.4 (2025-01-08)

- Fix URL comparison for Landing page conformance (#163, @gadomski)
- Fix `Search` validation when `datetime` is `None` (#165, @gadomski)

## 3.1.3 (2024-10-14)

- Add optional `numberMatched` and `numberReturned` to `api.collections.Collections` model to match the OGC Common part2 specification

## 3.1.2 (2024-08-20)

- Add more **MimeTypes** (geojsonseq, pbf, mvt, ndjson, openapi_yaml, pdf, csv, parquet)

## 3.1.1 (2024-07-09)

- Cache remote JSON schemas for extensions (#155, @avbentem)
- add `requests` and `jsonschema` in a **validation** optional dependencies (#156, @vincentsarago)

## 3.1.0 (2024-05-21)

- Allow extra fields in Links (#144, @jonhealy1)
- Remove the deprecated `Context` extension (#138, @vincentsarago)
- Rename `stac_pydantic.api.conformance.ConformanceClasses` to `stac_pydantic.api.conformance.Conformance`
- Update pre-commit configuration and switch to astral-sh/ruff for linter and formater
- Add official support for python 3.12
- Enforce required `type` key for `Collection` and `Catalog` models
- Add queryables link relation type (#123, @constantinius)
- Fix STAC API Query Extension operator names from ne->neq, le->lte, and ge->gte (#120, @philvarner)
- Better **datetime** parsing/validation by using Pydantic native types and remove `ciso8601` requirement (#131, @eseglem)
- move datetime validation in `StacCommonMetadata` model definition (#131, @eseglem)
- use `StacBaseModel` as base model for `Asset` model (#148, @vincentsarago)
- add `license` in `StacCommonMetadata` model (#147, @vincentsarago)
- make `limit` optional in `api.Search` model (#150, @vincentsarago)
- set `start/end datetime` to the datetime value when passing only one value in `api.Search` (#152, @vincentsarago)

## 3.0.0 (2024-01-25)

- Support pydantic>2.0 (@huard)

## 2.0.3 (2022-5-3)

- Allow item bbox to be null if item geometry is null (#108, @yellowcap)
- Include 'children' link relation (#112, @moradology)

## 2.0.2 (2021-11-22)

- Remove fields added by STAC API search extensions (#100, @rsmith013 & @moradology)
- Add ExtendedSearch class with fields from STAC API search extensions (#100, @rsmith013 & @moradology)
- Allow for non-ellipsis open temporal windows (#103, @moradology)
- Add the canonical and service-doc relation types (#104, @moradology)

## 2.0.1 (2021-07-08)

- Add bbox validator to STAC search (#95, @geospatialjeff)
- Fix LandPage to make valid STAC 1.0 catalog (#96, @lossyrob)

## 2.0.0 (2020-06-29)

- Add Collections model (#81, @moradology)
- Update to stac version 1.0.0 (#86, @moradology)
- Remove models for STAC spec extensions (#86, @moradology)
- Add conformsTo to LandingPage (#90, @moradology)

## 1.3.9 (2021-03-02)

- Add id to landing page, making it a valid catalog (#43, @lossyrob)
- Make `item_assets` (item assets extension) a dictionary of assets (#47, @kylebarron)
- Add pre-commit to CI (#48, @kylebarron)
- Add a `Links` model with custom root type to represent a list of links (#52)
- Move link related models to their own file (#53)
- Add link factories for generating inferred links (#55)
- Switch from relative to absolute imports (#61)
- Serialize date type fields to `datetime.datetime` upon model creation (#62)

## 1.3.9 (2020-03-02)

- Add id to landing page, making it a valid catalog (#43, @lossyrob)
- Make `item_assets` (item assets extension) a dictionary of assets (#47, @kylebarron)
- Add pre-commit to CI (#48, @kylebarron)
- Add a `Links` model with custom root type to represent a list of links (#52)
- Move link related models to their own file (#53)
- Add link factories for generating inferred links (#55)
- Switch from relative to absolute imports (#61)
- Serialize date type fields to `datetime.datetime` upon model creation (#62)

## 1.3.8 (2020-11-21)

- Remove enum restriction for asset roles (#39).
- Remove enum restriction for band common name (#40).

## 1.3.7 (2020-11-15)

- Rename `proj` extension to `projection` (#34).
- Remove `stac_extensions` enum requirement (#35).

## 1.3.6 (2020-09-11)

- Publish mypy type hints (#30)
- Correct Cloud Optimized GeoTiff mime type (#31)

## 1.3.5 (2020-09-09)

- Add `created` and `updated` to stac common metadata, fix aliases. (#28)

## 1.3.4 (2020-09-09)

- Update to stac version 1.0.0-beta.2 (#26)

## 1.2.4 (2020-09-08)

- Update to stac version 1.0.0-beta.1 (#24)

## 1.1.4 (2020-08-18)

- Fix multiple inheritance of stac extensions (#20)
- Properly instantiate lru_cache (found by @francbartoli, #21)

## 1.1.3 (2020-08-10)

- Add item model factory (#13)
- Add pre-commit hooks (#14)
- Add CLI for validating items (#15)
- Add option to skip validation of remote extensions (#16)
- Add helper function for item validation (#17)

## 1.0.3 (2020-06-03)

- Bugfixes (#10)
- Add rel types enum (#11)

## 1.0.2 (2020-06-02)

- Add models for the STAC API spec (#7)

## 1.0.1 (2020-05-21)

- Allow extra asset-level fields (#1)
- Fix population by field name model config, allowing model creation without extension namespaces (#2)
- Add enum of commonly used asset media types (#3)
- Move geojson models to `geojson-pydantic` library (#4)
