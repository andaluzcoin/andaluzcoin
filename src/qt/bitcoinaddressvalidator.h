// Copyright (c) 2011-2020 The Andaluzcoin Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#ifndef BITCOIN_QT_BITCOINADDRESSVALIDATOR_H
#define BITCOIN_QT_BITCOINADDRESSVALIDATOR_H

#include <QValidator>

/** Base58 entry widget validator, checks for valid characters and
 * removes some whitespace.
 */
class AndaluzcoinAddressEntryValidator : public QValidator
{
    Q_OBJECT

public:
    explicit AndaluzcoinAddressEntryValidator(QObject *parent);

    State validate(QString &input, int &pos) const override;
};

/** Andaluzcoin address widget validator, checks for a valid andaluzcoin address.
 */
class AndaluzcoinAddressCheckValidator : public QValidator
{
    Q_OBJECT

public:
    explicit AndaluzcoinAddressCheckValidator(QObject *parent);

    State validate(QString &input, int &pos) const override;
};

#endif // BITCOIN_QT_BITCOINADDRESSVALIDATOR_H
