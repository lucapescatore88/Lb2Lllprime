#include "Cluster.h"

#include <iostream>
#include <vector>



void Cluster::AddChannel(const unsigned int uplNumber, const unsigned int chanNumber, const double adcValue)
{
    Channel c;
    c.Uplink = uplNumber;
    c.ChannelNumber = chanNumber;
    c.AdcValue = adcValue;
    RelatedChannels.push_back(c);
}

void Cluster::RemoveChannel(const unsigned int chanNumber)
{
    for(std::vector<Channel>::iterator chan = RelatedChannels.begin(); chan != RelatedChannels.end(); ++chan)
    {
        if(chan->ChannelNumber == chanNumber)
        {
            RelatedChannels.erase(chan);
            return;
        }
    }
    std::cerr << "Cluster::RemoveChannel: Channel number " << chanNumber << " not in cluster -> cannot remove." << std::endl;
}

void Cluster::Resize(const unsigned int newsize)
{
    while(RelatedChannels.size() > newsize)
    {
        std::cout << "Current cluster size is " << RelatedChannels.size() << " max size is " << newsize << " -> reducing" << std::endl;
        if(RelatedChannels.front().AdcValue > RelatedChannels.back().AdcValue) RelatedChannels.pop_back();
        else RelatedChannels.erase(RelatedChannels.begin());
    }
}

double Cluster::GetChargeWeightedMean() const
{
    double totalCharge{0.};
    double mean{0.};
    for(const auto& chan : RelatedChannels)
    {
        mean += static_cast<double>(chan.ChannelNumber) * chan.AdcValue;
        totalCharge += chan.AdcValue;
    }
    return mean/totalCharge;
}

double Cluster::GetChargeWeightedMeanPacific(std::vector<float>thresholds) const
{
    return GetChargeWeightedMeanPacific(thresholds[0], thresholds[1], thresholds[2]);
}

double Cluster::GetChargeWeightedMeanPacific(double neighborW, double seedW, double sumW) const
{
    double totalCharge{0.};
    double mean{0.};
    for(const auto& chan : RelatedChannels)
    {
        double adc = 0.;
        if (chan.AdcValue == 1) adc = neighborW;
        else if (chan.AdcValue == 2) adc = seedW;
        else if (chan.AdcValue == 3) adc = sumW;

        mean += static_cast<double>(chan.ChannelNumber) * adc;
        totalCharge += adc;
    }
    return mean/totalCharge;
}


double Cluster::GetHitWeightedMean() const
{
    double mean{0.};
    for(const auto& chan : RelatedChannels)
    {
        mean += chan.ChannelNumber;
    }
    return mean/static_cast<double>(RelatedChannels.size());
}

double Cluster::GetSumOfAdcValues() const
{
    double sumOfAdcValues{0.};
    for(const auto& chan : RelatedChannels)
    {
        sumOfAdcValues += chan.AdcValue;
    }
    return sumOfAdcValues;
}

double Cluster::GetSumOfAdcValuesPacific(std::vector<float>thresholds) const
{
    return GetSumOfAdcValuesPacific(thresholds[0], thresholds[1], thresholds[2]);
}

double Cluster::GetSumOfAdcValuesPacific(double neighborW, double seedW, double sumW) const
{
    double sumOfAdcValues{0.};
    for(const auto& chan : RelatedChannels)
    {
        if (chan.AdcValue == 1) sumOfAdcValues += neighborW;
        else if (chan.AdcValue == 2) sumOfAdcValues += seedW;
        else if (chan.AdcValue == 3) sumOfAdcValues += sumW;
    }
    return sumOfAdcValues;
}



double Cluster::GetMaximumAdcValue() const
{
    double maxAdcValue{0.};
    for(const auto& chan : RelatedChannels)
    {
        if(chan.AdcValue > maxAdcValue) 
            maxAdcValue = chan.AdcValue;
    }
    return maxAdcValue;
}


unsigned int Cluster::GetMinChannel() const
{
    unsigned int minChannel{9999999};
    for(const auto& chan : RelatedChannels)
    {
        if(chan.ChannelNumber < minChannel) 
            minChannel = chan.ChannelNumber;
    }
    return minChannel;
}

unsigned int Cluster::GetMaxChannel() const
{
    unsigned int maxChannel{0};
    for(const auto& chan : RelatedChannels)
    {
        if(chan.ChannelNumber > maxChannel) 
            maxChannel = chan.ChannelNumber;
    }
    return maxChannel;
}

unsigned int Cluster::GetSeedChannelNumber() const
{
    double maxAdcValue{0.};
    unsigned int ChannelNumber = 9999;
    for(const auto& chan : RelatedChannels)
    {
        if(chan.AdcValue > maxAdcValue)
        {
            maxAdcValue = chan.AdcValue;
            ChannelNumber = chan.ChannelNumber;
        }
    }
    return ChannelNumber;
}


